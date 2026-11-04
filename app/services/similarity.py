from __future__ import annotations

import math
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Product, ProductEmbedding


@dataclass(frozen=True)
class SimilarProduct:
    product: Product
    score: float


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(sum(value * value for value in right))
    if denominator == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / denominator


def find_similar_products(db: Session, product_id: str, limit: int = 10) -> list[SimilarProduct]:
    source = db.get(ProductEmbedding, product_id)
    if source is None:
        return []

    if db.bind and db.bind.dialect.name == "postgresql":
        distance = ProductEmbedding.embedding.cosine_distance(source.embedding).label("distance")
        rows = db.execute(
            select(Product, distance)
            .join(ProductEmbedding, Product.id == ProductEmbedding.product_id)
            .where(Product.id != product_id, Product.available.is_(True))
            .order_by(distance)
            .limit(limit)
        ).all()
        return [SimilarProduct(product=product, score=max(0.0, min(1.0, 1.0 - float(distance_value)))) for product, distance_value in rows]

    candidates = db.scalars(select(Product).join(ProductEmbedding, Product.id == ProductEmbedding.product_id).where(Product.id != product_id, Product.available.is_(True))).all()
    scored = []
    for product in candidates:
        embedding = db.get(ProductEmbedding, product.id)
        score = _cosine_similarity(source.embedding, embedding.embedding) if embedding else 0.0
        scored.append(SimilarProduct(product=product, score=max(0.0, min(1.0, score))))
    return sorted(scored, key=lambda result: result.score, reverse=True)[:limit]

