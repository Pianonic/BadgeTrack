import pytest
from httpx import AsyncClient
import os
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set TESTING env var before importing the app
os.environ["TESTING"] = "true"

from src.main import app
from src.models import db, Badge, Cookie, initialize_database, close_database

@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Fixture to set up and tear down the database for each test function."""
    initialize_database()
    yield
    db.drop_tables([Badge, Cookie])
    close_database()

@pytest.fixture(scope="function")
async def client():
    """Fixture to create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_homepage(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

async def test_about_page(client: AsyncClient):
    response = await client.get("/about")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "timestamp" in response.json()
    assert response.json()["status"] == "healthy"

async def test_badge_creation_and_visit(client: AsyncClient):
    # First visit
    response = await client.get("/badge?tag=test-project")
    assert response.status_code == 200 # follows redirect
    assert "visitor_id" in response.cookies
    
    badge = Badge.get(Badge.tag == "test-project")
    assert badge.visits == 1

    # Second visit with same cookie
    visitor_id = response.cookies["visitor_id"]
    response2 = await client.get("/badge?tag=test-project", cookies={"visitor_id": visitor_id})
    assert response2.status_code == 200
    
    badge = Badge.get(Badge.tag == "test-project")
    assert badge.visits == 1 # Should not increment

    # Third visit with no cookie (new visitor)
    response3 = await client.get("/badge?tag=test-project")
    assert response3.status_code == 200
    
    badge = Badge.get(Badge.tag == "test-project")
    assert badge.visits == 2 # Should increment

async def test_get_tag_stats(client: AsyncClient):
    await client.get("/badge?tag=stats-test")
    await client.get("/badge?tag=stats-test")

    response = await client.get("/api/stats/stats-test")
    assert response.status_code == 200
    data = response.json()
    assert data["tag"] == "stats-test"
    assert data["visit_count"] == 2

async def test_get_system_stats(client: AsyncClient):
    await client.get("/badge?tag=system-stats-1")
    await client.get("/badge?tag=system-stats-2")
    await client.get("/badge?tag=system-stats-2")

    response = await client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tracked_tags"] == 2
    assert data["total_visits"] == 3
    assert data["new_badges_today"] == 2

async def test_app_info(client: AsyncClient):
    response = await client.get("/api/app-info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data
    assert data["environment"] == "Development"
