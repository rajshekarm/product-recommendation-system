import logging
from datetime import datetime, timezone
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.dependencies import verified_user_id
from app.models import Product, User, UserInteraction
from app.schemas import InteractionCreate, InteractionResponse, ProductCreate, ProductResponse, ProductUpdate, SimilarProductResponse, UserCreate, UserResponse
from app.services.product_embeddings import generate_product_embedding
from app.services.similarity import find_similar_products

logging.basicConfig(level=get_settings().log_level)
app = FastAPI(title="Fashion Recommendation Service", version="0.1.0", description="Phase 1 catalog and activity API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), caller_id: str = Depends(verified_user_id)):
    if payload.id != caller_id:
        raise HTTPException(status_code=403, detail="Cannot create a different user")
    user = User(id=payload.id)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")
    return user


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product already exists")
    if product.image_url:
        background_tasks.add_task(generate_product_embedding, product.id, str(product.image_url))
    return product


@app.get("/products", response_model=list[ProductResponse])
def list_products(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return db.scalars(select(Product).order_by(Product.created_at.desc()).offset(offset).limit(limit)).all()


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/products/{product_id}/similar", response_model=list[SimilarProductResponse])
def similar_products(product_id: str, limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    if not db.get(Product, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return [{"product": result.product, "score": result.score} for result in find_similar_products(db, product_id, limit)]


@app.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, payload: ProductUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    if product.image_url and ("image_url" in payload.model_dump(exclude_unset=True) or product.embedding is None):
        background_tasks.add_task(generate_product_embedding, product.id, str(product.image_url))
    return product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()


@app.post("/interactions", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db), caller_id: str = Depends(verified_user_id)):
    if payload.user_id != caller_id:
        raise HTTPException(status_code=403, detail="Cannot submit an interaction for a different user")
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    interaction = UserInteraction(**payload.model_dump(exclude_none=True), occurred_at=payload.occurred_at or datetime.now(timezone.utc), weight=get_settings().interaction_weights[payload.interaction_type])
    db.add(interaction)
    try:
        db.commit()
        db.refresh(interaction)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate event_id")
    return interaction


@app.get("/users/{user_id}/interactions", response_model=list[InteractionResponse])
def list_interactions(user_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), caller_id: str = Depends(verified_user_id)):
    if user_id != caller_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's interactions")
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return db.scalars(select(UserInteraction).where(UserInteraction.user_id == user_id).order_by(UserInteraction.occurred_at.desc()).offset(offset).limit(limit)).all()

