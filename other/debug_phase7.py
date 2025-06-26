#!/usr/bin/env python3
"""
Debug script to test Phase 7 API with detailed logging
"""

import sys
import os
import json
import time

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper

def test_scraper_initialization():
    """Test if the scraper initializes correctly"""
    print("=== Testing Scraper Initialization ===")
    
    try:
        scraper = InstagramProfileScraper()
        print("✅ Scraper instance created")
        
        # Test initialization
        print("Attempting to initialize scraper...")
        init_result = scraper.initialize()
        
        if init_result:
            print("✅ Scraper initialized successfully")
            print(f"Current account: {scraper.session_data.get('current_account', 'Unknown')}")
            
            # Test profile scraping
            print("\n=== Testing Profile Scraping ===")
            profile_data = scraper.scrape_profile("malangraya_info")
            
            if profile_data:
                print("✅ Profile data extracted:")
                print(json.dumps(profile_data, indent=2))
                
                # Test post scraping
                print("\n=== Testing Post Scraping ===")
                posts_data = scraper.scrape_posts(post_count=2, comment_count=2)
                
                print(f"Posts extracted: {len(posts_data)}")
                if posts_data:
                    print("✅ Posts data extracted:")
                    for i, post in enumerate(posts_data[:2]):
                        print(f"Post {i+1}: {post.get('urlPost', 'No URL')}")
                else:
                    print("❌ No posts extracted")
                    
            else:
                print("❌ Failed to extract profile data")
                
        else:
            print("❌ Failed to initialize scraper")
            
        # Clean up
        scraper.cleanup()
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

def test_api_validation():
    """Test API validation logic"""
    print("\n=== Testing API Validation ===")
    
    try:
        from api_server import InstagramScrapingAPI
        
        api = InstagramScrapingAPI()
        print("✅ API server instance created")
        
        # Test validation with valid data
        valid_data = {
            "suspected_account": "malangraya_info",
            "post_count": 5,
            "comment_count": 3
        }
        
        result = api._validate_request(valid_data)
        if not result['error']:
            print("✅ Validation with valid data successful")
            print(f"Validated account: {result['suspected_account']}")
            print(f"Validated post count: {result['post_count']}")
            print(f"Validated comment count: {result['comment_count']}")
        else:
            print(f"❌ Validation failed: {result['message']}")
            
        # Test with invalid data
        invalid_data = {
            "post_count": -5,
            "comment_count": "invalid"
        }
        
        result = api._validate_request(invalid_data)
        if result['error']:
            print("✅ Validation correctly rejected invalid data")
            print(f"Error message: {result['message']}")
        else:
            print("❌ Validation should have failed but didn't")
            
    except Exception as e:
        print(f"❌ Error during validation testing: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    print("=== Phase 7 Debug Script ===")
    print("This script will test the core functionality step by step")
    print()
    
    # Test initialization first
    test_api_validation()
    
    # Ask user if they want to test full scraping (requires browser)
    response = input("\nDo you want to test full scraping (requires Chrome/ChromeDriver)? (y/N): ").strip().lower()
    
    if response == 'y' or response == 'yes':
        test_scraper_initialization()
    else:
        print("Skipping full scraping test")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    main()
