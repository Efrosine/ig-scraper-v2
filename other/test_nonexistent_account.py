#!/usr/bin/env python3
"""
Test for completely non-existent Instagram account
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

def test_nonexistent_account():
    """Test searching for a completely non-existent account"""
    
    print("🔍 Testing Phase 5 - Non-existent Account Search")
    print("=" * 60)
    
    # Use a very random string that definitely doesn't exist
    test_account = "xyzabc123nonexistent999account"
    
    print(f"\n🎯 Testing search for non-existent account: @{test_account}")
    print("-" * 50)
    
    scraper = Phase5InstagramScraper()
    
    try:
        result = scraper.run_suspected_account_search(
            account_username=test_account,
            post_count=3,
            comment_count=2
        )
        
        print(f"✅ Search completed for @{test_account}")
        
        # Analyze the result
        if "error" in result:
            print(f"❌ Error detected: {result['error']}")
            if "not exist" in result['error'].lower() or "not found" in result['error'].lower():
                print("   → Account confirmed as non-existent")
            elif "Sorry, this page isn't available" in result['error']:
                print("   → Account page not available (likely deleted/suspended)")
            elif "User not found" in result['error'].lower():
                print("   → User not found error")
        else:
            posts_count = len(result.get('results', []))
            print(f"✅ Search successful - Found {posts_count} posts")
        
        # Save result
        output_file = f"/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2/output/nonexistent_test_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"📄 Result saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Non-existent Account Test")
    
    try:
        result = test_nonexistent_account()
        print("\n" + "=" * 60)
        print("🏁 Test Completed!")
        print("📊 Result shows how our system handles truly non-existent accounts")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
