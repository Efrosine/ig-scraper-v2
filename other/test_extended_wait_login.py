#!/usr/bin/env python3
"""
Test Login with Extended Wait Times
This script tests the improved login process with longer wait times.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper

def test_login_with_extended_waits():
    """Test login process with extended wait times."""
    print("=== Testing Login with Extended Wait Times ===")
    
    logger = setup_logging()
    
    # Create session manager
    session_manager = SessionManager()
    
    print(f"Available accounts:")
    for i, account in enumerate(session_manager.accounts):
        print(f"  {i}: {account['username']}")
    
    # Clear all existing sessions to ensure fresh login
    for account in session_manager.accounts:
        session_manager.clear_session(account['username'])
        print(f"Cleared session for: {account['username']}")
    
    # Create scraper
    scraper = InstagramScraper()
    
    try:
        print(f"\n=== Testing with Extended Wait Times ===")
        print(f"Wait timeout: {scraper.wait_timeout} seconds")
        print(f"Login process will include:")
        print(f"  - 5 second wait after page navigation")
        print(f"  - 2 second waits between input actions")
        print(f"  - 10 second wait after form submission")
        print(f"  - Up to 3 retry attempts with 8 second waits")
        print(f"  - 5 second wait in login success check")
        
        start_time = time.time()
        
        # Test login with backup support
        login_success = scraper.login_with_backup_support()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\nTotal login attempt time: {total_time:.2f} seconds")
        
        if login_success:
            current_account = session_manager.get_current_account()
            print(f"✅ Login successful with account: {current_account['username']}")
            
            # Check current URL
            current_url = scraper.driver.current_url
            print(f"Current URL: {current_url}")
            
            # Take screenshot
            scraper.take_screenshot("extended_wait_login_success.png")
            print("📸 Success screenshot saved")
            
            # Additional verification
            print("\n=== Additional Verification ===")
            scraper.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            final_url = scraper.driver.current_url
            print(f"Final verification URL: {final_url}")
            
            if "instagram.com/accounts/login" not in final_url and "auth_platform/codeentry" not in final_url:
                print("✅ Login verification successful with extended waits")
                return True
            else:
                print("❌ Login verification failed even with extended waits")
                return False
                
        else:
            print("❌ All accounts failed to login even with extended wait times")
            
            # Check final URL
            current_url = scraper.driver.current_url
            print(f"Failed login URL: {current_url}")
            
            # Take screenshot for debugging
            scraper.take_screenshot("extended_wait_login_failed.png")
            print("📸 Debug screenshot saved")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during extended wait login test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Take error screenshot
        if scraper.driver:
            scraper.take_screenshot("extended_wait_login_error.png")
            current_url = scraper.driver.current_url
            print(f"Error URL: {current_url}")
        
        return False
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    success = test_login_with_extended_waits()
    if success:
        print("\n🎉 Extended wait times helped with login!")
    else:
        print("\n😞 Login still failed even with extended wait times.")
