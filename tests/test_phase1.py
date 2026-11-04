def test_product_crud_and_pagination(client):
    response = client.post("/products", json={"id": "p1", "name": "Black Tee", "category": "t-shirts", "price_cents": 2500})
    assert response.status_code == 201
    assert response.json()["name"] == "Black Tee"
    assert client.get("/products/p1").status_code == 200
    assert client.patch("/products/p1", json={"color": "black"}).json()["color"] == "black"
    assert len(client.get("/products?limit=1").json()) == 1
    assert client.get("/products/missing").status_code == 404


def test_interaction_weight_authorization_and_duplicate_protection(client):
    assert client.post("/users", headers={"X-User-ID": "u1"}, json={"id": "u1"}).status_code == 201
    client.post("/products", json={"id": "p1", "name": "Black Tee", "category": "t-shirts"})
    event = {"event_id": "evt-1", "user_id": "u1", "product_id": "p1", "interaction_type": "add_to_cart"}
    created = client.post("/interactions", headers={"X-User-ID": "u1"}, json=event)
    assert created.status_code == 201
    assert created.json()["weight"] == 5
    assert client.post("/interactions", headers={"X-User-ID": "u1"}, json=event).status_code == 409
    assert client.get("/users/u1/interactions", headers={"X-User-ID": "u2"}).status_code == 403
    assert len(client.get("/users/u1/interactions", headers={"X-User-ID": "u1"}).json()) == 1


def test_validation_and_missing_dependencies(client):
    assert client.post("/interactions", headers={"X-User-ID": "u1"}, json={"event_id": "e", "user_id": "u1", "product_id": "p", "interaction_type": "invalid"}).status_code == 422
    assert client.post("/interactions", headers={"X-User-ID": "u1"}, json={"event_id": "e", "user_id": "u1", "product_id": "p", "interaction_type": "view"}).status_code == 404
    assert client.get("/users/u1/interactions").status_code == 401

