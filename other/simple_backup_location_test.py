#!/usr/bin/env python3
"""
Simple Backup Account Location Search Test
This script forces the use of backup account and tests location search.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager
from main import InstagramProfileScraper

def test_backup_location_search():
    """Test location search with backup account."""
    print("=== Testing Location Search with Backup Account ===")
    
    # Create scraper instance
    scraper = InstagramProfileScraper()
    
    # Force backup account usage
    session_manager = scraper.scraper.session_manager
    
    print(f"Primary account: {session_manager.accounts[0]['username']}")
    print(f"Backup account: {session_manager.accounts[1]['username']}")
    
    # Clear primary account session to force backup
    session_manager.clear_session(session_manager.accounts[0]['username'])
    print(f"Cleared session for primary account: {session_manager.accounts[0]['username']}")
    
    # Manually switch to backup account
    backup_account = session_manager.switch_to_backup_account()
    print(f"Switched to backup account: {backup_account['username']}")
    
    try:
        # Initialize scraper with backup account
        print("\nInitializing scraper with backup account...")
        if scraper.initialize():
            current_account = session_manager.get_current_account()
            print(f"✅ Successfully initialized with account: {current_account['username']}")
            
            # Run location search
            print("\n=== Running Location Search ===")
            location = "Malang"
            post_count = 5
            comment_count = 3
            
            result = scraper.search_by_location(location, post_count, comment_count)
            
            if result and "results" in result and result["results"]:
                print(f"✅ Location search successful! Found {len(result['results'])} posts")
                
                # Print first few posts
                for i, post in enumerate(result["results"][:3]):
                    username = post.get("usernamePost", "Unknown")
                    url = post.get("urlPost", "No URL")
                    caption = post.get("caption", "No caption")[:100] + "..." if len(post.get("caption", "")) > 100 else post.get("caption", "No caption")
                    print(f"  Post {i+1}: @{username}")
                    print(f"    URL: {url}")
                    print(f"    Caption: {caption}")
                    print()
                
                # Save results
                output_file = f"output/backup_location_search_results_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 Results saved to: {output_file}")
                
                return True
                
            else:
                print("❌ Location search failed - no posts found")
                print(f"Result: {result}")
                return False
                
        else:
            print("❌ Failed to initialize scraper with backup account")
            return False
            
    except Exception as e:
        print(f"❌ Error during backup location search: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Close scraper
        if scraper.scraper:
            scraper.scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_backup_location_search()
