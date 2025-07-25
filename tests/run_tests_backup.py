#!/usr/bin/env python3
"""
Test runner for BadgeTrack - runs all tests
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n[RUN] {description}")
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[PASS] {description} - PASSED")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {description} - FAILED")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] {description} - ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("BadgeTrack Test Runner")
    print("=" * 50)
    
    # Change to the project root directory (parent of tests)
    root_dir = Path(__file__).parent.parent
    os.chdir(root_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Set environment variables
    os.environ["TESTING"] = "true"
    if not os.environ.get("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    
    test_results = []    # Test 1: Simple unit tests
    test_results.append(run_command(
        ["py", "tests/test_simple.py"],
        "Unit Tests (Database & Core Logic)"
    ))    # Test 2: Try running FastAPI tests directly (avoiding pytest conflicts)
    test_results.append(run_command(
        ["py", "tests/test_main_simple.py"],
        "FastAPI Integration Tests (Direct)"
    ))
      # Test 3: Server integration tests (optional)
    print("\n[NOTE] Cookie integration tests require a running server")
    print("   Start server with: py wsgi.py")
    print("   Then run: py tests/test_cookies.py")
      # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    
    for i, result in enumerate(test_results, 1):
        status = "[PASS]" if result else "[FAIL]"
        print(f"   Test {i}: {status}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
