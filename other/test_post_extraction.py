#!/usr/bin/env python3
"""
Test script focused on post link extraction
"""

import sys
import os
import time

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper

def test_post_extraction():
    """Test post link extraction specifically"""
    print("=== Testing Post Link Extraction ===")
    
    try:
        scraper = InstagramProfileScraper()
        print("✅ Scraper instance created")
        
        # Initialize
        if not scraper.initialize():
            print("❌ Failed to initialize scraper")
            return
        
        print("✅ Scraper initialized")
        
        # Navigate to profile
        profile_data = scraper.scrape_profile("malangraya_info")
        if not profile_data:
            print("❌ Failed to navigate to profile")
            return
            
        print(f"✅ Navigated to profile, found {profile_data.get('posts_count', 0)} posts")
        
        # Now test the parser directly
        from parser import InstagramPostParser
        
        parser = InstagramPostParser()
        print("✅ Parser created")
        
        # Test post link extraction
        print("Testing post link extraction...")
        post_links = parser._get_post_links(scraper.scraper.driver, 5)
        
        print(f"Extracted {len(post_links)} post links:")
        for i, link in enumerate(post_links[:3]):
            print(f"  {i+1}. {link}")
            
        if post_links:
            print("✅ Post link extraction successful!")
            
            # Test extracting data from first post
            print(f"\nTesting single post extraction from: {post_links[0]}")
            post_data = parser._extract_single_post_data(scraper.scraper.driver, post_links[0], 2)
            
            if post_data:
                print("✅ Single post extraction successful!")
                print(f"Username: {post_data.get('usernamePost', 'N/A')}")
                print(f"Caption: {post_data.get('caption', 'N/A')[:100]}...")
                print(f"Comments: {len(post_data.get('comments', {}))}")
            else:
                print("❌ Single post extraction failed")
        else:
            print("❌ No post links extracted")
            
        # Cleanup
        scraper.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_post_extraction()
