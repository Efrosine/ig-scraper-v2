#!/usr/bin/env python3
"""
Test Backup Account Login with Improved Error Detection
This script tests the improved login failure detection including auth platform code entry.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper

def test_backup_login_with_error_detection():
    """Test backup account login with improved error detection."""
    print("=== Testing Backup Account Login with Error Detection ===")
    
    logger = setup_logging()
    
    # Create session manager and force backup account
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
        print("\n=== Testing Login with All Accounts ===")
        
        login_success = scraper.login_with_backup_support()
        
        if login_success:
            current_account = session_manager.get_current_account()
            print(f"✅ Login successful with account: {current_account['username']}")
            
            # Check current URL for any issues
            current_url = scraper.driver.current_url
            print(f"Current URL: {current_url}")
            
            # Additional checks for login status
            if "instagram.com/auth_platform/codeentry" in current_url:
                print("❌ ERROR: Account redirected to code entry - login actually failed!")
            elif "instagram.com/accounts/login" in current_url:
                print("❌ ERROR: Still on login page - login actually failed!")
            elif any(pattern in current_url.lower() for pattern in ["challenge", "two_factor", "checkpoint", "suspend", "confirm"]):
                print(f"❌ ERROR: Suspicious URL detected: {current_url}")
            else:
                print("✅ Login verification successful - no error patterns detected")
                
                # Take screenshot
                scraper.take_screenshot("backup_login_verified.png")
                print("📸 Screenshot saved")
                
                # Test basic functionality
                print("\n=== Testing Basic Navigation ===")
                scraper.driver.get("https://www.instagram.com/")
                time.sleep(3)
                
                final_url = scraper.driver.current_url
                print(f"Final URL: {final_url}")
                
                if "instagram.com/auth_platform/codeentry" in final_url:
                    print("❌ ERROR: Redirected to code entry during navigation")
                else:
                    print("✅ Navigation successful")
                    
        else:
            print("❌ All accounts failed to login")
            
            # Check what page we ended up on
            current_url = scraper.driver.current_url
            print(f"Failed login URL: {current_url}")
            
            if "instagram.com/auth_platform/codeentry" in current_url:
                print("ℹ️ Account(s) redirected to code entry page - likely flagged or requires verification")
            
            # Take screenshot for debugging
            scraper.take_screenshot("login_failed_debug.png")
            print("📸 Debug screenshot saved")
            
    except Exception as e:
        print(f"❌ Error during login test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Take error screenshot
        if scraper.driver:
            scraper.take_screenshot("login_error_debug.png")
            current_url = scraper.driver.current_url
            print(f"Error URL: {current_url}")
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_backup_login_with_error_detection()
