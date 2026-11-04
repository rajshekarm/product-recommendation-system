from __future__ import annotations

from pathlib import Path
from typing import Any
from PIL import Image


class EmbeddingError(RuntimeError):
    """Raised when a product image cannot be converted into an embedding."""


def normalize_vector(values: list[float]) -> list[float]:
    """Return an L2-normalized vector suitable for cosine similarity."""
    if not values:
        raise ValueError("Cannot normalize an empty vector")
    norm = sum(value * value for value in values) ** 0.5
    if norm == 0:
        raise ValueError("Cannot normalize a zero vector")
    return [value / norm for value in values]


class FashionClipEmbedder:
    """Lazy FashionCLIP image encoder.

    The model is loaded only on the first call to ``embed_image``. This keeps
    API startup fast and makes the class straightforward to replace with a
    mocked encoder in tests.
    """

    def __init__(self, model_id: str = "patrickjohncyh/fashion-clip", device: str | None = None):
        self.model_id = model_id
        self.device = device
        self._processor: Any = None
        self._model: Any = None
        self._torch: Any = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor
            self._torch = torch
            self._processor = CLIPProcessor.from_pretrained(self.model_id)
            self._model = CLIPModel.from_pretrained(self.model_id)
            target_device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
            self._model = self._model.to(target_device).eval()
            self.device = target_device
        except Exception as exc:  # model/download errors need a stable service-level error
            raise EmbeddingError(f"Unable to load FashionCLIP model '{self.model_id}'") from exc

    def embed_image(self, image: Image.Image) -> list[float]:
        if not isinstance(image, Image.Image):
            raise TypeError("image must be a PIL.Image.Image")
        self._load()
        try:
            inputs = self._processor(images=image.convert("RGB"), return_tensors="pt")
            inputs = {key: value.to(self.device) for key, value in inputs.items()}
            with self._torch.inference_mode():
                features = self._model.get_image_features(**inputs)
            values = features.detach().float().cpu().tolist()[0]
            return normalize_vector(values)
        except Exception as exc:
            raise EmbeddingError("Unable to generate a FashionCLIP image embedding") from exc

    def embed_file(self, path: str | Path) -> list[float]:
        try:
            with Image.open(path) as image:
                return self.embed_image(image)
        except EmbeddingError:
            raise
        except Exception as exc:
            raise EmbeddingError(f"Unable to read product image '{path}'") from exc

