#!/usr/bin/env python3
"""
Phase 7 API Demo - Demonstrates the HTTP endpoint functionality
"""

import requests
import json
import time
import sys

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    try:
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_scrape_endpoint(base_url):
    """Test the scrape endpoint with minimal data"""
    try:
        print("Testing scrape endpoint...")
        
        # Test with minimal request (uses defaults)
        test_data = {
            "suspected_account": "malangraya_info",
            "post_count": 2,  # Small number for testing
            "comment_count": 2
        }
        
        print(f"Sending request: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for scraping
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Scrape request successful!")
            print(f"Results: {len(data.get('results', []))} posts extracted")
            return True
        else:
            try:
                error_data = response.json()
                print(f"❌ Scrape request failed: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"❌ Scrape request failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Scrape request error: {e}")
        return False

def test_validation_errors(base_url):
    """Test validation error handling"""
    try:
        print("Testing validation errors...")
        
        # Test with invalid data
        invalid_data = {
            "post_count": -5,  # Invalid: negative
            "comment_count": "invalid"  # Invalid: not integer
        }
        
        response = requests.post(
            f"{base_url}/scrape",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            error_data = response.json()
            print(f"✅ Validation error correctly handled: {error_data.get('message', 'Unknown error')}")
            return True
        else:
            print(f"❌ Expected validation error, got: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation test error: {e}")
        return False

def main():
    """Main demo function"""
    print("=== Phase 7 API Demo ===")
    print()
    
    base_url = "http://localhost:5000"
    
    print(f"Testing API at: {base_url}")
    print("Make sure the server is running with: python 'phase files/phase7_scraper.py'")
    print()
    
    # Wait a moment to let user start server if needed
    print("Starting tests in 3 seconds...")
    time.sleep(3)
    
    tests = [
        ("Health Check", lambda: test_health_endpoint(base_url)),
        ("Validation Errors", lambda: test_validation_errors(base_url)),
        # Note: Full scraping test is commented out as it requires real Instagram login
        # ("Scrape Endpoint", lambda: test_scrape_endpoint(base_url))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print(f"=== Demo Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 API demo successful!")
        print()
        print("Example API calls:")
        example_calls = [
            f"curl -X GET {base_url}/health",
            f"curl -X POST {base_url}/scrape -H 'Content-Type: application/json' -d '{{\"suspected_account\": \"malangraya_info\", \"post_count\": 5, \"comment_count\": 3}}'"
        ]
        
        for i, call in enumerate(example_calls, 1):
            print(f"{i}. {call}")
    else:
        print("❌ Some tests failed. Please check the server status.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
