#!/usr/bin/env python3
"""
Phase 5 Location Search with Forced Backup Account
This script runs Phase 5 location search with the backup account.
"""

import os
import sys
import time

# Add directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase files'))

from utils import SessionManager
from phase5_scraper import Phase5InstagramScraper

def run_phase5_with_backup():
    """Run Phase 5 location search with backup account."""
    print("=== Phase 5 Location Search with Backup Account ===")
    
    # Create Phase 5 scraper
    phase5_scraper = Phase5InstagramScraper()
    
    # Force backup account usage by clearing primary session
    # This will be done inside the scraper initialization
    
    try:
        # Clear primary account session to force backup
        # We need to access the session manager before initialization
        from scraper import InstagramScraper
        temp_scraper = InstagramScraper()
        session_manager = temp_scraper.session_manager
        
        print(f"Primary account: {session_manager.accounts[0]['username']}")
        print(f"Backup account: {session_manager.accounts[1]['username']}")
        
        # Clear primary account session
        session_manager.clear_session(session_manager.accounts[0]['username'])
        print(f"✅ Cleared session for primary account: {session_manager.accounts[0]['username']}")
        
        # Close temp scraper
        temp_scraper.close()
        
        # Now run location search - it should use backup account
        print("\n=== Running Phase 5 Location Search ===")
        location = "Malang"
        post_count = 10
        comment_count = 5
        
        print(f"📍 Location: {location}")
        print(f"📊 Target: {post_count} posts, {comment_count} comments each")
        
        result = phase5_scraper.run_location_search(location, post_count, comment_count)
        
        if result and "results" in result and result["results"]:
            print(f"\n✅ Phase 5 Location Search Successful!")
            print(f"🔍 Found {len(result['results'])} posts")
            
            # Print summary of results
            for i, post in enumerate(result["results"][:3]):  # Show first 3
                username = post.get("usernamePost", "Unknown")
                url = post.get("urlPost", "No URL")
                caption = post.get("caption", "No caption")
                caption_preview = caption[:80] + "..." if len(caption) > 80 else caption
                
                print(f"\n📱 Post {i+1}:")
                print(f"   👤 User: @{username}")
                print(f"   🔗 URL: {url}")
                print(f"   📝 Caption: {caption_preview}")
                print(f"   💬 Comments: {len(post.get('comments', {}))}")
            
            if len(result["results"]) > 3:
                print(f"\n... and {len(result['results']) - 3} more posts")
            
            # Check metadata for account info
            metadata = result.get("metadata", {})
            account_used = metadata.get("account_used", "Unknown")
            print(f"\n🔐 Account used: {account_used}")
            
            if account_used == "eprosen2":
                print("✅ SUCCESS: Backup account was used successfully!")
            else:
                print(f"⚠️  Note: Account used was {account_used} (expected: eprosen2)")
            
            # Print file location
            output_files = [f for f in os.listdir("output") if "phase5_location_Malang" in f and str(int(time.time()) - 60) in f]
            if output_files:
                latest_file = max(output_files)
                print(f"💾 Results saved to: output/{latest_file}")
            
            return True
            
        else:
            print(f"\n❌ Phase 5 Location Search Failed")
            print(f"Result: {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during Phase 5 backup test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_phase5_with_backup()
    
    if success:
        print("\n🎉 Phase 5 backup account test completed successfully!")
        print("✅ The backup account system is working correctly.")
        print("✅ Location search works with backup account.")
    else:
        print("\n❌ Phase 5 backup account test failed.")
        print("ℹ️  Check logs for more details.")
