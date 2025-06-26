#!/usr/bin/env python3
"""
Force Backup Account Test Script
This script will force the scraper to use the backup account by clearing the primary account session.
"""

import os
import sys
import time
import logging

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper

def clear_primary_account_session():
    """Clear the primary account session to force backup usage."""
    session_manager = SessionManager()
    primary_account = session_manager.accounts[0]  # Get primary account
    
    print(f"Primary account: {primary_account['username']}")
    print(f"Backup account: {session_manager.accounts[1]['username']}")
    
    # Clear primary account session
    session_manager.clear_session(primary_account['username'])
    print(f"Cleared session for primary account: {primary_account['username']}")
    
    return session_manager

def test_backup_account_login():
    """Test login with backup account by forcing failure of primary."""
    logger = setup_logging()
    
    print("=== Testing Backup Account Login ===")
    
    # Clear primary account session
    session_manager = clear_primary_account_session()
    
    # Create scraper instance
    scraper = InstagramScraper()
    
    try:
        print("\nAttempting login with backup support...")
        
        # Try to login - this should fail on primary and succeed on backup
        login_success = scraper.login_with_backup_support()
        
        if login_success:
            current_account = session_manager.get_current_account()
            print(f"✅ Login successful with account: {current_account['username']}")
            
            # Verify we're logged in
            scraper.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Take screenshot to verify
            scraper.take_screenshot("backup_account_login_test.png")
            print("📸 Screenshot saved as backup_account_login_test.png")
            
            # Check current URL
            current_url = scraper.driver.current_url
            print(f"Current URL: {current_url}")
            
            if "instagram.com/accounts/login" not in current_url:
                print("✅ Successfully logged in (not on login page)")
            else:
                print("❌ Still on login page - backup login may have failed")
                
        else:
            print("❌ All accounts failed to login")
            
    except Exception as e:
        print(f"❌ Error during backup account test: {str(e)}")
        logger.error(f"Backup account test failed: {str(e)}")
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_backup_account_login()
