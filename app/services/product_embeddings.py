from __future__ import annotations

import logging
from io import BytesIO
from urllib.request import Request, urlopen

from PIL import Image
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import ProductEmbedding
from app.services.embedding import FashionClipEmbedder

logger = logging.getLogger(__name__)
_embedder = FashionClipEmbedder()


def generate_product_embedding(product_id: str, image_url: str, embedder: FashionClipEmbedder | None = None) -> None:
    """Download one catalog image, embed it, and upsert its vector.

    This function creates its own short-lived database session because it is
    designed to run after the HTTP response in a background task.
    """
    db: Session = SessionLocal()
    try:
        request = Request(image_url, headers={"User-Agent": "fashion-recommendation-service/0.1"})
        with urlopen(request, timeout=20) as response:  # noqa: S310 - image hosts must be restricted in production
            image = Image.open(BytesIO(response.read()))
            vector = (embedder or _embedder).embed_image(image)

        record = db.get(ProductEmbedding, product_id)
        if record is None:
            record = ProductEmbedding(product_id=product_id, embedding=vector, model_name=(embedder or _embedder).model_id)
            db.add(record)
        else:
            record.embedding = vector
            record.model_name = (embedder or _embedder).model_id
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Product embedding generation failed for product_id=%s", product_id)
    finally:
        db.close()

