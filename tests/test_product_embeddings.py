from app.services.product_embeddings import generate_product_embedding


def test_product_embedding_job_logs_failures_without_raising(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("network unavailable")

    monkeypatch.setattr("app.services.product_embeddings.urlopen", fail)
    generate_product_embedding("missing-product", "https://example.com/image.jpg")

