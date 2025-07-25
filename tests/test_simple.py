import os
import sys
import asyncio
import tempfile
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set testing environment
os.environ["TESTING"] = "true"

from src.models import initialize_database, close_database, Badge, Cookie, db
from src.services import update_visit_count, get_tag_visit_count, get_system_statistics

def test_database_setup():
    """Test database initialization"""
    print("Testing database setup...")
    result = initialize_database()
    assert result, "Database initialization failed"
    print("(checkmark) Database initialized successfully")

def test_visit_tracking():
    """Test visit tracking functionality"""
    print("Testing visit tracking...")
    
    # Test first visit (should create new badge and increment)
    count1, incremented1, cookie1 = update_visit_count(None, "test-project")
    assert count1 == 1, f"Expected count 1, got {count1}"
    assert incremented1 == True, "First visit should increment"
    assert cookie1 is not None, "Should generate new cookie"
    print(f"(checkmark) First visit: count={count1}, incremented={incremented1}, cookie={cookie1[:8]}...")
    
    # Test second visit with same cookie (should NOT increment)
    count2, incremented2, cookie2 = update_visit_count(cookie1, "test-project")
    assert count2 == 1, f"Expected count 1, got {count2}"
    assert incremented2 == False, "Second visit with same cookie should not increment"
    print(f"(checkmark) Second visit with same cookie: count={count2}, incremented={incremented2}")
    
    # Test third visit with different cookie (should increment)
    count3, incremented3, cookie3 = update_visit_count(None, "test-project")
    assert count3 == 2, f"Expected count 2, got {count3}"
    assert incremented3 == True, "Third visit with new cookie should increment"
    assert cookie3 != cookie1, "Should generate different cookie"
    print(f"(checkmark) Third visit with new cookie: count={count3}, incremented={incremented3}")

def test_tag_stats():
    """Test tag statistics retrieval"""
    print("Testing tag statistics...")
    
    # Create some test data
    update_visit_count(None, "stats-test-1")
    update_visit_count(None, "stats-test-1")
    update_visit_count(None, "stats-test-2")
    
    count1 = get_tag_visit_count("stats-test-1")
    count2 = get_tag_visit_count("stats-test-2")
    count_nonexistent = get_tag_visit_count("nonexistent-tag")
    
    assert count1 == 2, f"Expected count 2 for stats-test-1, got {count1}"
    assert count2 == 1, f"Expected count 1 for stats-test-2, got {count2}"
    assert count_nonexistent == 0, f"Expected count 0 for nonexistent tag, got {count_nonexistent}"
    
    print(f"(checkmark) Tag stats: stats-test-1={count1}, stats-test-2={count2}, nonexistent={count_nonexistent}")

def test_system_stats():
    """Test system statistics"""
    print("Testing system statistics...")
    
    stats = get_system_statistics()
    assert "total_tracked_tags" in stats, "System stats should include total_tracked_tags"
    assert "total_visits" in stats, "System stats should include total_visits"
    assert "new_badges_today" in stats, "System stats should include new_badges_today"
    assert stats["total_tracked_tags"] >= 0, "Total tracked tags should be non-negative"
    assert stats["total_visits"] >= 0, "Total visits should be non-negative"
    
    print(f"(checkmark) System stats: {stats}")

def cleanup_database():
    """Clean up test database"""
    print("Cleaning up test database...")
    try:
        db.drop_tables([Badge, Cookie])
        close_database()
        print("(checkmark) Database cleaned up successfully")
    except Exception as e:
        print(f"⚠ Warning during cleanup: {e}")

def main():
    """Run all tests"""
    print("Starting BadgeTrack functionality tests...\n")
    
    try:
        test_database_setup()
        test_visit_tracking()
        test_tag_stats()
        test_system_stats()
        
        print("\nAll tests passed! The application is working correctly.")
        return 0
        
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1
    finally:
        cleanup_database()

if __name__ == "__main__":
    exit(main())
