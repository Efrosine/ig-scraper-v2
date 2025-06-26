#!/usr/bin/env python3
"""
Direct Backup Account Test
This script directly tests location search with backup account after forcing account switch.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from scraper import InstagramScraper
from location_search import LocationSearcher

def test_direct_backup_location_search():
    """Test location search directly with backup account."""
    print("=== Direct Backup Account Location Search Test ===")
    
    logger = setup_logging()
    
    # Create session manager and force backup account
    session_manager = SessionManager()
    
    print(f"Primary account: {session_manager.accounts[0]['username']}")
    print(f"Backup account: {session_manager.accounts[1]['username']}")
    
    # Clear primary account session
    session_manager.clear_session(session_manager.accounts[0]['username'])
    print(f"Cleared session for primary account")
    
    # Force switch to backup account
    backup_account = session_manager.switch_to_backup_account()
    print(f"Switched to backup account: {backup_account['username']}")
    
    # Create scraper
    scraper = InstagramScraper()
    
    try:
        # Setup driver
        scraper._setup_driver()
        
        # Login with backup account
        print(f"\nAttempting login with backup account: {backup_account['username']}")
        
        login_success = scraper.login_with_account(backup_account)
        
        if login_success:
            print(f"✅ Login successful with backup account: {backup_account['username']}")
            
            # Take screenshot
            scraper.take_screenshot("backup_account_logged_in.png")
            
            # Create location searcher
            location_searcher = LocationSearcher(scraper.driver, logger)
            
            # Test location search
            print("\n=== Testing Location Search ===")
            location = "Malang"
            post_count = 5
            comment_count = 3
            
            print(f"Searching for posts in: {location}")
            print(f"Target: {post_count} posts, {comment_count} comments each")
            
            posts = location_searcher.search_by_location(location, post_count)
            
            if posts:
                print(f"✅ Location search successful! Found {len(posts)} posts with backup account")
                
                # Print results
                for i, post in enumerate(posts):
                    username = post.get("usernamePost", "Unknown")
                    url = post.get("urlPost", "No URL")
                    caption = post.get("caption", "No caption")
                    caption_preview = caption[:100] + "..." if len(caption) > 100 else caption
                    
                    print(f"\nPost {i+1}:")
                    print(f"  Username: @{username}")
                    print(f"  URL: {url}")
                    print(f"  Caption: {caption_preview}")
                    print(f"  Comments: {len(post.get('comments', {}))}")
                
                # Save results
                import json
                output_file = f"output/backup_direct_location_search_{int(time.time())}.json"
                
                result_data = {
                    "metadata": {
                        "search_type": "location",
                        "location": location,
                        "account_used": backup_account['username'],
                        "timestamp": time.time(),
                        "posts_requested": post_count,
                        "comments_requested": comment_count,
                        "posts_found": len(posts)
                    },
                    "results": posts
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 Results saved to: {output_file}")
                
                return True
                
            else:
                print("❌ Location search failed - no posts found with backup account")
                
                # Debug: Take screenshot of current page
                scraper.take_screenshot("backup_location_search_failed.png")
                print("📸 Debug screenshot saved")
                
                return False
                
        else:
            print("❌ Backup account login failed")
            scraper.take_screenshot("backup_login_failed.png")
            return False
            
    except Exception as e:
        print(f"❌ Error during direct backup test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Close scraper
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_direct_backup_location_search()
