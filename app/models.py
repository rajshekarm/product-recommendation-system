from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.types import JSON, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


class EmbeddingVector(TypeDecorator):
    """Native pgvector on PostgreSQL, JSON fallback for lightweight local tests."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and Vector is not None:
            return dialect.type_descriptor(Vector(512))
        return dialect.type_descriptor(JSON())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    interactions: Mapped[list["UserInteraction"]] = relationship(back_populates="user")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(120))
    color: Mapped[str | None] = mapped_column(String(80))
    style: Mapped[str | None] = mapped_column(String(80))
    image_url: Mapped[str | None] = mapped_column(String(2048))
    price_cents: Mapped[int | None] = mapped_column(Integer)
    available: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    embedding: Mapped["ProductEmbedding | None"] = relationship(back_populates="product", uselist=False)


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    __table_args__ = (UniqueConstraint("event_id", name="uq_user_interactions_event_id"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="interactions")
    product: Mapped[Product] = relationship()


class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(EmbeddingVector(), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    product: Mapped[Product] = relationship(back_populates="embedding")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    preference_vector: Mapped[list[float] | None] = mapped_column(EmbeddingVector())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

