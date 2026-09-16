import os

os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:27019")
os.environ.setdefault("DATABASE_NAME", "vitatwin_test")
os.environ.setdefault("JWT_SECRET", "vitatwin-test-secret-with-more-than-32-characters")
os.environ.setdefault("OPENAI_API_KEY", "")

import pytest
from fastapi.testclient import TestClient

from core.database import get_database
from main import app


@pytest.fixture(autouse=True)
def clean_database():
    db = get_database()
    db.users.delete_many({})
    db.checkins.delete_many({})
    yield
    db.users.delete_many({})
    db.checkins.delete_many({})


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def account(client):
    response = client.post("/api/v1/auth/register", json={"name": "Maya", "email": "maya@example.com", "password": "strongpass123"})
    assert response.status_code == 201
    data = response.json()
    return {"headers": {"Authorization": f"Bearer {data['access_token']}"}, "user": data["user"]}
