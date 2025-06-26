#!/usr/bin/env python3
"""
Simple test for suspended account handling in Phase 5
"""

import sys
import os
import time
import json

# Add the project root to Python path
sys.path.insert(0, '/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2')
sys.path.insert(0, '/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2/core files')
sys.path.insert(0, '/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2/phase files')

from phase5_scraper import Phase5InstagramScraper

def test_single_suspended_account():
    """Test searching for a single potentially suspended account"""
    
    print("🔍 Testing Phase 5 - Single Suspended Account Search")
    print("=" * 60)
    
    # Use a very generic name that likely doesn't exist or is suspended
    test_account = "suspended_user_test_123"
    
    print(f"\n🎯 Testing search for: @{test_account}")
    print("-" * 50)
    
    scraper = Phase5InstagramScraper()
    
    try:
        result = scraper.run_suspected_account_search(
            account_username=test_account,
            post_count=5,
            comment_count=3
        )
        
        print(f"✅ Search completed for @{test_account}")
        
        # Analyze the result
        if "error" in result:
            print(f"❌ Error detected: {result['error']}")
            if "not exist" in result['error'].lower():
                print("   → Account doesn't exist (likely suspended/deleted)")
            elif "private" in result['error'].lower():
                print("   → Account is private")
            elif "login" in result['error'].lower():
                print("   → Login issue (our account may be flagged)")
            elif "suspended" in result['error'].lower():
                print("   → Account is confirmed suspended")
        else:
            posts_count = len(result.get('results', []))
            print(f"✅ Found {posts_count} posts")
            if posts_count == 0:
                print("   → No posts found - account might be suspended, private, or empty")
        
        # Save result for detailed inspection
        output_file = f"/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2/output/suspended_single_test_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"📄 Result saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Single Suspended Account Test")
    
    try:
        result = test_single_suspended_account()
        print("\n" + "=" * 60)
        print("🏁 Test Completed!")
        print("📊 Check the output file and logs for detailed analysis")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
