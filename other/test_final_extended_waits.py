#!/usr/bin/env python3
"""
Test Location Search with Successful Backup Login
This script tests location search after successful backup login with extended waits.
"""

import os
import sys
import time

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from main import InstagramProfileScraper

def test_location_search_with_extended_waits():
    """Test location search with backup account using extended waits."""
    print("=== Testing Location Search with Extended Wait Times ===")
    
    # Clear primary account session to force backup usage
    session_manager = SessionManager()
    session_manager.clear_session(session_manager.accounts[0]['username'])
    print(f"Cleared primary account session to force backup usage")
    
    # Create scraper instance
    scraper = InstagramProfileScraper()
    
    try:
        print("\n=== Initializing Scraper with Extended Waits ===")
        start_time = time.time()
        
        if scraper.initialize():
            init_time = time.time() - start_time
            print(f"✅ Scraper initialized successfully in {init_time:.2f} seconds")
            
            current_account = scraper.scraper.session_manager.get_current_account()
            print(f"✅ Using account: {current_account['username']}")
            
            # Run location search
            print("\n=== Running Location Search ===")
            location = "Malang"
            post_count = 5
            comment_count = 3
            
            search_start = time.time()
            result = scraper.search_by_location(location, post_count, comment_count)
            search_time = time.time() - search_start
            
            print(f"Location search completed in {search_time:.2f} seconds")
            
            if result and "results" in result and result["results"]:
                print(f"✅ Location search successful! Found {len(result['results'])} posts")
                
                # Print results summary
                for i, post in enumerate(result["results"][:3]):
                    username = post.get("usernamePost", "Unknown")
                    url = post.get("urlPost", "No URL")
                    caption = post.get("caption", "No caption")
                    caption_preview = caption[:100] + "..." if len(caption) > 100 else caption
                    
                    print(f"\nPost {i+1}:")
                    print(f"  Username: @{username}")
                    print(f"  URL: {url[:50]}...")
                    print(f"  Caption: {caption_preview}")
                
                # Save results
                import json
                output_file = f"output/extended_wait_location_search_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 Results saved to: {output_file}")
                print(f"🎉 Extended wait times successfully enabled both login and location search!")
                
                return True
                
            else:
                print("❌ Location search failed despite successful login")
                print(f"Result: {result}")
                return False
                
        else:
            print("❌ Failed to initialize scraper even with extended waits")
            return False
            
    except Exception as e:
        print(f"❌ Error during location search test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Close scraper
        if scraper.scraper:
            scraper.scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    success = test_location_search_with_extended_waits()
    if success:
        print("\n🎉 SUCCESS: Extended wait times resolved the login issues!")
    else:
        print("\n😞 Issues remain despite extended wait times.")
