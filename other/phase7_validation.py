#!/usr/bin/env python3
"""
Simple validation test for Phase 7 implementation
"""

import sys
import os
import json

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

def test_api_server_import():
    """Test if we can import the API server"""
    try:
        from api_server import InstagramScrapingAPI
        print("✅ API server import successful")
        return True
    except Exception as e:
        print(f"❌ API server import failed: {e}")
        return False

def test_phase7_scraper_import():
    """Test if we can import Phase 7 scraper"""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))
        from phase7_scraper import Phase7InstagramScraper
        print("✅ Phase 7 scraper import successful")
        return True
    except Exception as e:
        print(f"❌ Phase 7 scraper import failed: {e}")
        return False

def test_validation_logic():
    """Test the validation logic"""
    try:
        from api_server import InstagramScrapingAPI
        api = InstagramScrapingAPI()
        
        # Test valid data
        valid_data = {
            "suspected_account": "test_account",
            "post_count": 5,
            "comment_count": 3
        }
        
        result = api._validate_request(valid_data)
        if result['error']:
            print(f"❌ Validation failed for valid data: {result['message']}")
            return False
        
        print("✅ Validation logic working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_environment_loading():
    """Test environment variable loading"""
    try:
        from utils import load_environment_variables
        env_vars = load_environment_variables()
        
        required_keys = ['DEFAULT_SUSPECTED_ACCOUNT', 'DEFAULT_POST_COUNT', 'FORWARDING_PORT']
        for key in required_keys:
            if key not in env_vars:
                print(f"❌ Missing environment variable: {key}")
                return False
        
        print("✅ Environment variable loading successful")
        return True
        
    except Exception as e:
        print(f"❌ Environment loading test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=== Phase 7 Validation Tests ===")
    print()
    
    tests = [
        test_api_server_import,
        test_phase7_scraper_import,
        test_validation_logic,
        test_environment_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All Phase 7 validation tests passed!")
        print()
        print("Phase 7 is ready! You can now:")
        print("1. Run the server: python 'phase files/phase7_scraper.py'")
        print("2. Test the API: curl -X GET http://localhost:5000/health")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
