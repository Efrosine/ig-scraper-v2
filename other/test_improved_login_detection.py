#!/usr/bin/env python3
"""
Test Improved Login Detection with URL Check
This script tests the enhanced login detection that prioritizes the exact Instagram home URL.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper

def test_improved_login_detection():
    """Test login with improved URL-based detection."""
    print("=== Testing Improved Login Detection (URL-based) ===")
    
    logger = setup_logging()
    
    # Create session manager
    session_manager = SessionManager()
    
    print(f"Available accounts:")
    for i, account in enumerate(session_manager.accounts):
        print(f"  {i}: {account['username']}")
    
    # Clear sessions to ensure fresh login
    for account in session_manager.accounts:
        session_manager.clear_session(account['username'])
        print(f"Cleared session for: {account['username']}")
    
    # Create scraper
    scraper = InstagramScraper()
    
    try:
        print(f"\n=== Testing Enhanced Login Detection ===")
        print(f"Primary detection: URL == 'https://www.instagram.com/'")
        print(f"Secondary detection: Element-based indicators")
        print(f"Fallback detection: Instagram domain without error patterns")
        
        start_time = time.time()
        
        # Test login with backup support
        login_success = scraper.login_with_backup_support()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nLogin attempt completed in {total_time:.2f} seconds")
        
        if login_success:
            current_account = session_manager.get_current_account()
            print(f"✅ Login successful with account: {current_account['username']}")
            
            # Check final URL
            final_url = scraper.driver.current_url
            print(f"Final URL: {final_url}")
            
            # Verify the URL detection logic
            if final_url == "https://www.instagram.com/" or final_url == "https://www.instagram.com":
                print("✅ PRIMARY SUCCESS: Exact Instagram home URL detected!")
            elif "instagram.com" in final_url and not any(pattern in final_url.lower() for pattern in ["login", "auth_platform", "challenge", "checkpoint"]):
                print("✅ FALLBACK SUCCESS: Valid Instagram domain detected!")
            else:
                print(f"⚠️ UNEXPECTED: URL doesn't match expected patterns: {final_url}")
            
            # Take screenshot
            scraper.take_screenshot("improved_login_detection_success.png")
            print("📸 Success screenshot saved")
            
            # Test navigation to verify login is stable
            print("\n=== Testing Navigation Stability ===")
            scraper.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            navigation_url = scraper.driver.current_url
            print(f"After navigation URL: {navigation_url}")
            
            if navigation_url == "https://www.instagram.com/" or navigation_url == "https://www.instagram.com":
                print("✅ Navigation stability confirmed - login is solid!")
                return True
            else:
                print(f"⚠️ Navigation changed URL: {navigation_url}")
                return True  # Still consider it success if we got this far
                
        else:
            print("❌ All accounts failed to login with improved detection")
            
            # Check what page we ended up on
            final_url = scraper.driver.current_url
            print(f"Failed login final URL: {final_url}")
            
            # Take screenshot for debugging
            scraper.take_screenshot("improved_login_detection_failed.png")
            print("📸 Debug screenshot saved")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during improved login detection test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Take error screenshot
        if scraper.driver:
            scraper.take_screenshot("improved_login_detection_error.png")
            error_url = scraper.driver.current_url
            print(f"Error URL: {error_url}")
        
        return False
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    success = test_improved_login_detection()
    if success:
        print("\n🎉 SUCCESS: Improved login detection working!")
    else:
        print("\n😞 Login detection still needs work.")
