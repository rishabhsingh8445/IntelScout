from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_liveness():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_database_url_normalization_neon_render():
    from src.config import Settings

    raw_neon_url = "postgresql://neondb_owner:npg_xyz@ep-art.neon.tech/neondb?sslmode=require&channel_binding=require"
    s = Settings(DATABASE_URL=raw_neon_url)
    assert s.DATABASE_URL.startswith("postgresql+asyncpg://")
    assert "ssl=require" in s.DATABASE_URL
    assert "sslmode" not in s.DATABASE_URL
    assert "channel_binding" not in s.DATABASE_URL
