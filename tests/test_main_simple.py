import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
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

def setup_test_db():
    """Set up test database"""
    initialize_database()
    print("Test database initialized")

def teardown_test_db():
    """Clean up test database"""
    try:
        db.drop_tables([Badge, Cookie])
        close_database()
    except Exception as e:
        print(f"Warning during teardown: {e}")

def test_homepage():
    """Test homepage returns 200"""
    print("Testing homepage...")
    # Initialize database before creating test client
    initialize_database()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "BadgeTrack" in response.text
    print("(checkmark) Homepage test passed")

def test_badge_endpoint_new_tag():
    """Test creating a new badge with a tag"""
    print("Testing badge creation...")
    # Initialize database before creating test client
    initialize_database()
    client = TestClient(app)
    response = client.get("/badge?tag=test-tag")
    assert response.status_code == 200
    assert "badge" in response.headers.get("content-type", "").lower()
    print("(checkmark) Badge creation test passed")

def test_badge_endpoint_with_cookie():
    """Test badge endpoint with existing cookie"""
    print("Testing badge with cookie...")
    # Initialize database before creating test client
    initialize_database()
    client = TestClient(app)
    # First request (new visitor)
    response1 = client.get("/badge?tag=cookie-test")
    assert response1.status_code == 200
    
    # Extract cookie from response
    cookies = response1.cookies
    
    # Second request with same cookie (should not increment)
    response2 = client.get("/badge?tag=cookie-test", cookies=cookies)
    assert response2.status_code == 200
    print("(checkmark) Cookie test passed")

def test_stats_endpoint():
    """Test stats endpoint"""
    print("Testing stats endpoint...")
    # Initialize database before creating test client
    initialize_database()
    client = TestClient(app)
    # Create some test data first
    client.get("/badge?tag=stats-test")
    
    # Test stats endpoint
    response = client.get("/stats?tag=stats-test")
    assert response.status_code == 200
    
    data = response.json()
    assert "tag" in data
    assert "visits" in data
    assert data["tag"] == "stats-test"
    assert data["visits"] >= 1
    print("(checkmark) Stats endpoint test passed")

def test_system_stats():
    """Test system stats endpoint"""
    print("Testing system stats...")
    # Initialize database before creating test client
    initialize_database()
    client = TestClient(app)
    response = client.get("/system-stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_tracked_tags" in data
    assert "total_visits" in data
    assert "new_badges_today" in data
    print("(checkmark) System stats test passed")

def run_all_tests():
    """Run all FastAPI integration tests"""
    print("Starting FastAPI integration tests...\n")
    
    try:
        # Set up database once at the beginning
        setup_test_db()
        
        test_homepage()
        test_badge_endpoint_new_tag()
        test_badge_endpoint_with_cookie()
        test_stats_endpoint()
        test_system_stats()
        
        print("\nAll FastAPI integration tests passed!")
        return 0
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        teardown_test_db()

def main():
    """Main test runner function"""
    return run_all_tests()

if __name__ == "__main__":
    exit(main())
