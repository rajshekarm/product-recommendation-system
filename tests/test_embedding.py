import math
import pytest
from PIL import Image
from app.services.embedding import EmbeddingError, FashionClipEmbedder, normalize_vector


def test_normalize_vector_returns_unit_length():
    result = normalize_vector([3.0, 4.0])
    assert result == [0.6, 0.8]
    assert math.isclose(sum(value * value for value in result), 1.0)


def test_normalize_vector_rejects_invalid_values():
    with pytest.raises(ValueError):
        normalize_vector([])
    with pytest.raises(ValueError):
        normalize_vector([0.0, 0.0])


def test_embedder_does_not_load_model_until_used():
    embedder = FashionClipEmbedder()
    assert embedder._model is None


def test_embedder_requires_pil_images():
    embedder = FashionClipEmbedder()
    with pytest.raises(TypeError):
        embedder.embed_image("not-an-image")

