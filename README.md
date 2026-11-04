# Real-Time AI Fashion Recommendation System

Phase 1 provides the catalog and user-activity foundation. It exposes a FastAPI service backed by PostgreSQL, with pgvector enabled for the embedding table used by later phases.

## Run locally

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open Swagger at <http://localhost:8000/docs>.

## Test

```powershell
python -m pip install -r requirements-dev.txt
pytest
```

For user-scoped endpoints, the current integration boundary is the `X-User-ID` header. The value must match the path/body user ID; replace this dependency with the e-commerce platform's verified JWT/session identity before production deployment.

