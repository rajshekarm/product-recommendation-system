from app.models import ProductEmbedding


def test_similar_products_are_ranked_and_filtered(client):
    client.post("/products", json={"id": "source", "name": "Source", "category": "tops"})
    client.post("/products", json={"id": "close", "name": "Close", "category": "tops"})
    client.post("/products", json={"id": "far", "name": "Far", "category": "tops"})
    client.post("/products", json={"id": "unavailable", "name": "Unavailable", "category": "tops", "available": False})

    from app.main import app
    session = app.state.test_session()
    try:
        session.add_all([
            ProductEmbedding(product_id="source", embedding=[1.0, 0.0], model_name="test"),
            ProductEmbedding(product_id="close", embedding=[0.9, 0.1], model_name="test"),
            ProductEmbedding(product_id="far", embedding=[0.0, 1.0], model_name="test"),
            ProductEmbedding(product_id="unavailable", embedding=[1.0, 0.0], model_name="test"),
        ])
        session.commit()
    finally:
        session.close()

    response = client.get("/products/source/similar?limit=2")
    assert response.status_code == 200
    assert [item["product"]["id"] for item in response.json()] == ["close", "far"]
    assert response.json()[0]["score"] > response.json()[1]["score"]


def test_similar_products_requires_existing_product(client):
    assert client.get("/products/missing/similar").status_code == 404

