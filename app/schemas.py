from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UserCreate(BaseModel):
    id: str = Field(min_length=1, max_length=128)


class UserResponse(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime


class ProductCreate(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=120)
    color: str | None = Field(default=None, max_length=80)
    style: str | None = Field(default=None, max_length=80)
    image_url: HttpUrl | None = None
    price_cents: int | None = Field(default=None, ge=0)
    available: bool = True


class ProductResponse(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    brand: str | None = Field(default=None, max_length=120)
    color: str | None = Field(default=None, max_length=80)
    style: str | None = Field(default=None, max_length=80)
    image_url: HttpUrl | None = None
    price_cents: int | None = Field(default=None, ge=0)
    available: bool | None = None


class SimilarProductResponse(BaseModel):
    product: ProductResponse
    score: float = Field(ge=0, le=1)


class InteractionCreate(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    product_id: str = Field(min_length=1, max_length=128)
    interaction_type: str = Field(pattern="^(view|virtual_try_on|mix_and_match|add_to_cart|purchase)$")
    occurred_at: datetime | None = None


class InteractionResponse(InteractionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    occurred_at: datetime
    weight: float
    created_at: datetime

