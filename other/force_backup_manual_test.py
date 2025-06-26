#!/usr/bin/env python3
"""
Force Backup Account Test Script - Advanced Version
This script will manually trigger backup account usage by simulating primary account failure.
"""

import os
import sys
import time
import logging

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper

def force_backup_account_usage():
    """Force the scraper to use backup account by manually advancing the account index."""
    logger = setup_logging()
    
    print("=== Forcing Backup Account Usage ===")
    
    # Create scraper instance
    scraper = InstagramScraper()
    
    # Manually advance to backup account
    session_manager = scraper.session_manager
    
    print(f"Available accounts: {len(session_manager.accounts)}")
    for i, account in enumerate(session_manager.accounts):
        print(f"  Account {i}: {account['username']}")
    
    print(f"Current account index: {session_manager.current_account_index}")
    print(f"Current account: {session_manager.get_current_account()['username']}")
    
    # Force switch to backup account
    backup_account = session_manager.switch_to_backup_account()
    if backup_account:
        print(f"Switched to backup account: {backup_account['username']}")
        print(f"New account index: {session_manager.current_account_index}")
    else:
        print("No backup account available")
        return
    
    try:
        print("\nAttempting login with backup account...")
        
        # Setup driver
        scraper._setup_driver()
        
        # Try to login with the backup account
        login_success = scraper.login_with_account(backup_account)
        
        if login_success:
            print(f"✅ Login successful with backup account: {backup_account['username']}")
            
            # Verify we're logged in
            scraper.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Take screenshot to verify
            scraper.take_screenshot("backup_account_manual_test.png")
            print("📸 Screenshot saved as backup_account_manual_test.png")
            
            # Check current URL
            current_url = scraper.driver.current_url
            print(f"Current URL: {current_url}")
            
            if "instagram.com/accounts/login" not in current_url:
                print("✅ Successfully logged in with backup account (not on login page)")
                
                # Test location search with backup account
                print("\n=== Testing Location Search with Backup Account ===")
                return test_location_search_with_backup(scraper)
                
            else:
                print("❌ Still on login page - backup login failed")
                
        else:
            print("❌ Backup account login failed")
            
    except Exception as e:
        print(f"❌ Error during backup account test: {str(e)}")
        logger.error(f"Backup account test failed: {str(e)}")
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

def test_location_search_with_backup(scraper):
    """Test location search functionality with the backup account."""
    try:
        from location_search import LocationSearch
        
        print("Initializing location search...")
        location_search = LocationSearch(scraper.driver, scraper.logger)
        
        # Test location search for Malang
        location = "Malang"
        post_count = 5
        comment_count = 3
        
        print(f"Searching for posts in location: {location}")
        print(f"Target posts: {post_count}, Comments per post: {comment_count}")
        
        posts = location_search.search_by_location(location, post_count, comment_count)
        
        if posts:
            print(f"✅ Found {len(posts)} posts with backup account!")
            for i, post in enumerate(posts):
                print(f"  Post {i+1}: {post.get('usernamePost', 'Unknown')} - {post.get('urlPost', 'No URL')}")
            return True
        else:
            print("❌ No posts found with backup account")
            
            # Take screenshot of current page for debugging
            scraper.take_screenshot("backup_location_search_debug.png")
            print("📸 Debug screenshot saved as backup_location_search_debug.png")
            return False
            
    except Exception as e:
        print(f"❌ Error during location search test: {str(e)}")
        scraper.logger.error(f"Location search test failed: {str(e)}")
        return False

if __name__ == "__main__":
    force_backup_account_usage()
