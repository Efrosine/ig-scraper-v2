#!/usr/bin/env python3
"""
Simple test script to verify Phase 1 functionality without actual Instagram login.
This demonstrates the scraper initialization and basic functionality.
"""

import sys
import os

# Add core files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from utils import SessionManager, RateLimiter, setup_logging
from scraper import InstagramScraper
from main import InstagramProfileScraper

def test_session_manager():
    """Test session manager functionality."""
    print("Testing SessionManager...")
    
    # Test account loading
    session_manager = SessionManager()
    print(f"✓ Loaded {session_manager.get_account_count()} accounts")
    
    # Test current account
    current = session_manager.get_current_account()
    print(f"✓ Current account: {current['username']}")
    
    # Test backup switching
    remaining = session_manager.get_remaining_accounts()
    print(f"✓ Remaining backup accounts: {remaining}")
    
    return True

def test_rate_limiter():
    """Test rate limiter functionality."""
    print("Testing RateLimiter...")
    
    rate_limiter = RateLimiter()
    print(f"✓ Request delay: {rate_limiter.request_delay}s")
    print(f"✓ Login delay: {rate_limiter.login_delay}s")
    
    return True

def test_logging_setup():
    """Test logging setup."""
    print("Testing logging setup...")
    
    logger = setup_logging()
    logger.info("Test log message")
    print("✓ Logging configured successfully")
    
    return True

def test_scraper_initialization():
    """Test scraper initialization without actual WebDriver."""
    print("Testing InstagramScraper initialization...")
    
    scraper = InstagramScraper()
    print("✓ InstagramScraper created successfully")
    
    # Test session manager integration
    assert scraper.session_manager is not None
    print("✓ Session manager integrated")
    
    # Test rate limiter integration  
    assert scraper.rate_limiter is not None
    print("✓ Rate limiter integrated")
    
    return True

def test_main_scraper():
    """Test main scraper class."""
    print("Testing InstagramProfileScraper...")
    
    main_scraper = InstagramProfileScraper()
    print("✓ InstagramProfileScraper created successfully")
    
    # Test session info structure
    session_info = main_scraper.get_session_info()
    assert "status" in session_info
    assert "timestamp" in session_info
    print("✓ Session info structure correct")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("📸 INSTAGRAM PROFILE SCRAPER - PHASE 1 VERIFICATION")
    print("=" * 60)
    print("Running functionality tests without Instagram connection...\n")
    
    tests = [
        ("Session Manager", test_session_manager),
        ("Rate Limiter", test_rate_limiter),
        ("Logging Setup", test_logging_setup),
        ("Scraper Initialization", test_scraper_initialization),
        ("Main Scraper", test_main_scraper),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 {test_name}:")
            print("-" * 30)
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Phase 1 foundation is working correctly.")
        print("Ready for Instagram login testing.")
        return True
    else:
        print(f"\n⚠️  {failed} TESTS FAILED!")
        print("Please fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
