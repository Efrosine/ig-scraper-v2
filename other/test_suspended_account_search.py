#!/usr/bin/env python3
"""
Test script for searching suspended/banned Instagram accounts
This will test if our Phase 5 implementation properly handles suspended accounts
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

def test_suspended_account_search():
    """Test searching for suspended/banned accounts"""
    
    print("🔍 Testing Phase 5 - Suspended Account Search")
    print("=" * 60)
    
    # Test cases for potentially suspended accounts
    test_accounts = [
        "suspended_test_user",  # Common pattern for suspended accounts
        "banned_user_123",      # Another common pattern
        "fake_account_test",    # Often gets suspended
        "spam_bot_account",     # Spam accounts often suspended
        "deleted_user_2024"     # Deleted/suspended pattern
    ]
    
    scraper = Phase5InstagramScraper()
    
    for account in test_accounts:
        print(f"\n🎯 Testing search for potentially suspended account: @{account}")
        print("-" * 50)
        
        try:
            # Test suspected account search
            result = scraper.run_suspected_account_search(
                account_username=account,
                post_count=5,
                comment_count=3
            )
            
            print(f"✅ Search completed for @{account}")
            
            # Check if we detected account issues
            if "error" in result:
                print(f"❌ Error detected: {result['error']}")
                if "not exist" in result['error'].lower() or "private" in result['error'].lower():
                    print("   → This might be a suspended/deleted account")
                elif "login" in result['error'].lower():
                    print("   → Login issue detected (account may be flagged)")
            else:
                print(f"✅ Found {len(result.get('results', []))} posts")
                if len(result.get('results', [])) == 0:
                    print("   → No posts found - account might be suspended or private")
            
            # Save result for inspection
            output_file = f"/home/bahrul_maghfiroh_4mzone/aiproject/ig-scraper-v2/output/suspended_test_{account}_{int(time.time())}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"📄 Result saved to: {output_file}")
            
            # Wait between tests to avoid being flagged
            print("⏳ Waiting 30 seconds before next test...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Exception during test for @{account}: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print("🏁 Suspended Account Search Test Completed")
    print("   Check the output files and logs for detailed results")

def test_real_suspended_account():
    """Test with a potentially real suspended account"""
    
    print("\n🔍 Testing with potentially real suspended account patterns")
    print("=" * 60)
    
    # These are common patterns that often get suspended
    real_test_patterns = [
        "instagramuser123456789",  # Generic long usernames often get suspended
        "follow4follow_bot",       # Bot-like names
        "buyigfollowers2024",     # Commercial spam accounts
    ]
    
    scraper = Phase5InstagramScraper()
    
    for account in real_test_patterns:
        print(f"\n🎯 Testing real pattern: @{account}")
        
        try:
            result = scraper.run_suspected_account_search(
                account_username=account,
                post_count=3,
                comment_count=2
            )
            
            print(f"Result for @{account}:")
            if "error" in result:
                print(f"  ❌ {result['error']}")
            else:
                print(f"  ✅ Posts found: {len(result.get('results', []))}")
            
            time.sleep(15)  # Shorter wait for real tests
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            continue

if __name__ == "__main__":
    print("🚀 Starting Suspended Account Search Tests")
    print("This will test our Phase 5 system's ability to handle suspended accounts")
    
    try:
        # First test with fake suspended account patterns
        test_suspended_account_search()
        
        # Then test with more realistic patterns
        test_real_suspended_account()
        
        print("\n✅ All suspended account tests completed!")
        print("📊 Check logs and output files for detailed analysis")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
