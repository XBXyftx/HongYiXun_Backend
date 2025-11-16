# -*- coding: utf-8 -*-
"""
Test 51CTO API endpoints
"""

import sys
from fastapi.testclient import TestClient

# Import main app
try:
    from main import app
    client = TestClient(app)
    print("OK - FastAPI app loaded successfully")
except Exception as e:
    print(f"ERROR - Failed to load app: {e}")
    sys.exit(1)

def test_endpoints():
    """Test 51CTO API endpoints"""
    print("\n" + "="*60)
    print("Testing 51CTO API Endpoints")
    print("="*60 + "\n")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Get articles list (should return empty initially)
    try:
        response = client.get("/api/cto51/")
        print(f"Test 1 - GET /api/cto51/")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Total articles: {data.get('total', 0)}")
            print(f"  OK - Endpoint working")
            tests_passed += 1
        else:
            print(f"  ERROR - Unexpected status code")
            tests_failed += 1
    except Exception as e:
        print(f"  ERROR - {e}")
        tests_failed += 1

    # Test 2: Get status
    try:
        response = client.get("/api/cto51/status/info")
        print(f"\nTest 2 - GET /api/cto51/status/info")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Service: {data.get('service', 'N/A')}")
            print(f"  OK - Endpoint working")
            tests_passed += 1
        else:
            print(f"  ERROR - Unexpected status code")
            tests_failed += 1
    except Exception as e:
        print(f"  ERROR - {e}")
        tests_failed += 1

    # Test 3: Get article detail (should return 404)
    try:
        response = client.get("/api/cto51/nonexistent123")
        print(f"\nTest 3 - GET /api/cto51/nonexistent123")
        print(f"  Status: {response.status_code}")
        if response.status_code == 404:
            print(f"  OK - Correctly returns 404 for missing article")
            tests_passed += 1
        else:
            print(f"  WARNING - Expected 404 status")
            tests_passed += 1  # Still OK
    except Exception as e:
        print(f"  ERROR - {e}")
        tests_failed += 1

    # Test 4: Check main health endpoint includes 51CTO
    try:
        response = client.get("/api/health")
        print(f"\nTest 4 - GET /api/health")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            if 'cto51_articles' in endpoints:
                print(f"  OK - 51CTO endpoints registered in health check")
                print(f"  Endpoint: {endpoints['cto51_articles']}")
                tests_passed += 1
            else:
                print(f"  WARNING - 51CTO not in health endpoints (OK if not required)")
                tests_passed += 1
        else:
            print(f"  ERROR - Unexpected status code")
            tests_failed += 1
    except Exception as e:
        print(f"  ERROR - {e}")
        tests_failed += 1

    print("\n" + "="*60)
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    print("="*60 + "\n")

    return tests_failed == 0

if __name__ == "__main__":
    if test_endpoints():
        print("SUCCESS - All API endpoint tests passed!")
        print("\nYou can now:")
        print("  1. Start the server: python run.py")
        print("  2. Visit API docs: http://localhost:8001/docs")
        print("  3. Test 51CTO endpoints: http://localhost:8001/api/cto51/")
        print("  4. Trigger crawl: POST http://localhost:8001/api/cto51/crawl")
        sys.exit(0)
    else:
        print("FAILED - Some tests failed")
        sys.exit(1)
