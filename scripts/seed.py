from app.db import SessionLocal
from app.models import Product, User
from app.schemas import InteractionCreate
from app.main import create_interaction


def seed():
    db = SessionLocal()
    try:
        if not db.get(User, "demo-user"):
            db.add(User(id="demo-user"))
        products = [
            Product(id="demo-black-tee", name="Black Oversized Tee", category="t-shirts", color="black", style="streetwear", price_cents=2500),
            Product(id="demo-blue-jeans", name="Relaxed Blue Jeans", category="jeans", color="blue", style="casual", price_cents=6500),
            Product(id="demo-white-sneakers", name="White Sneakers", category="shoes", color="white", style="casual", price_cents=8000),
        ]
        for product in products:
            if not db.get(Product, product.id):
                db.add(product)
        db.commit()
        print("Seeded demo catalog and user. Submit interactions through POST /interactions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

