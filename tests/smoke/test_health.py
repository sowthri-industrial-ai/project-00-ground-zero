"""Tier 2 · Smoke · /health ping."""
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.mark.smoke
def test_health_endpoint_returns_200():
    with TestClient(app) as c:
        r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
