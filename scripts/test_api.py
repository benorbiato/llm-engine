#!/usr/bin/env python3
"""
Test script for Judicial Process Verification API.
Tests different scenarios: approved, rejected, and incomplete processes.
"""

import requests
import json
from pathlib import Path


def test_health(base_url: str) -> bool:
    """Test health endpoint."""
    print("Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error during health check: {e}")
        return False


def test_process(base_url: str, example_file: str, description: str) -> bool:
    """Test process verification."""
    print(f"\nTesting {description}...")
    
    try:
        with open(example_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        
        response = requests.post(
            f"{base_url}/verify/",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Verification successful")
            print(f"  Decision: {result['decision']}")
            print(f"  Process: {result['numeroProcesso']}")
            print(f"  Rationale: {result['rationale'][:100]}...")
            print(f"  Citations: {result['citations']}")
            return True
        else:
            print(f"✗ Verification failed with status {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
    
    except FileNotFoundError:
        print(f"✗ Test file not found: {example_file}")
        return False
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        return False


def main():
    """Main test execution."""
    base_url = "http://localhost:8000"
    examples_dir = Path("./examples")
    
    print("=" * 60)
    print("Judicial Process Verification API - Test Suite")
    print("=" * 60)
    
    # Health check
    if not test_health(base_url):
        print("\n✗ Cannot connect to API. Ensure it's running on localhost:8000")
        return False
    
    # Test different scenarios
    tests = [
        (
            examples_dir / "test_process_approved.json",
            "Approved Process Verification"
        ),
        (
            examples_dir / "test_process_rejected_labor.json",
            "Rejected Process (Labor Sphere)"
        ),
        (
            examples_dir / "test_process_incomplete.json",
            "Incomplete Process Verification"
        ),
    ]
    
    results = []
    for test_file, description in tests:
        results.append(test_process(base_url, str(test_file), description))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return True
    else:
        print(f"✗ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

