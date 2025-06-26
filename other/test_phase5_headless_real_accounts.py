#!/usr/bin/env python3
"""
Phase 5 Final Test - Headless Mode with Real Accounts
This script tests the complete Phase 5 functionality in headless mode using real accounts from .env
"""

import os
import sys
import time
import json

# Add the core files directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core files'))

from utils import SessionManager, setup_logging
from main import InstagramProfileScraper

def test_phase5_headless_real_accounts():
    """Test Phase 5 functionality in headless mode with real accounts."""
    print("=== Phase 5 Final Test - Headless Mode with Real Accounts ===")
    
    logger = setup_logging()
    
    # Create session manager to check accounts
    session_manager = SessionManager()
    
    print(f"Loaded accounts from .env:")
    for i, account in enumerate(session_manager.accounts):
        print(f"  {i+1}: {account['username']}")
    
    # Clear all sessions for fresh test
    for account in session_manager.accounts:
        session_manager.clear_session(account['username'])
        print(f"Cleared session for: {account['username']}")
    
    print(f"\n=== Testing in HEADLESS mode ===")
    print(f"Browser will run without GUI")
    print(f"Using real accounts from .env file")
    
    # Test both search types
    test_results = {
        "suspected_account_search": None,
        "location_search": None,
        "total_test_time": 0,
        "login_account_used": None
    }
    
    start_time = time.time()
    
    try:
        # Test 1: Suspected Account Search
        print("\n" + "="*60)
        print("TEST 1: SUSPECTED ACCOUNT SEARCH")
        print("="*60)
        
        suspected_account = "malangraya_info"
        post_count = 5
        comment_count = 3
        
        print(f"Target: @{suspected_account}")
        print(f"Posts: {post_count}, Comments: {comment_count}")
        
        scraper1 = InstagramProfileScraper()
        
        search1_start = time.time()
        
        if scraper1.initialize():
            current_account = scraper1.scraper.session_manager.get_current_account()
            test_results["login_account_used"] = current_account['username']
            print(f"✅ Logged in with: {current_account['username']}")
            
            result1 = scraper1.search_by_suspected_account(suspected_account, post_count, comment_count)
            
            search1_time = time.time() - search1_start
            
            if result1 and "results" in result1 and result1["results"]:
                print(f"✅ Suspected account search successful!")
                print(f"   Found {len(result1['results'])} posts")
                print(f"   Time: {search1_time:.2f} seconds")
                
                # Save results
                output_file1 = f"output/phase5_final_suspected_account_{int(time.time())}.json"
                with open(output_file1, 'w', encoding='utf-8') as f:
                    json.dump(result1, f, ensure_ascii=False, indent=2)
                
                test_results["suspected_account_search"] = {
                    "success": True,
                    "posts_found": len(result1["results"]),
                    "time": search1_time,
                    "output_file": output_file1
                }
                
                # Print first post as example
                if result1["results"]:
                    first_post = result1["results"][0]
                    print(f"   Example post: @{first_post.get('usernamePost', 'Unknown')}")
                    print(f"   Caption: {first_post.get('caption', 'No caption')[:100]}...")
                
            else:
                print(f"❌ Suspected account search failed")
                test_results["suspected_account_search"] = {
                    "success": False,
                    "error": "No posts found",
                    "time": search1_time
                }
        else:
            print(f"❌ Failed to initialize scraper for suspected account search")
            test_results["suspected_account_search"] = {
                "success": False,
                "error": "Initialization failed",
                "time": 0
            }
        
        # Close first scraper
        if scraper1.scraper:
            scraper1.scraper.close()
        
        print(f"\nWaiting 10 seconds between tests...")
        time.sleep(10)
        
        # Test 2: Location Search
        print("\n" + "="*60)
        print("TEST 2: LOCATION SEARCH")
        print("="*60)
        
        location = "Malang"
        
        print(f"Target: {location}")
        print(f"Posts: {post_count}, Comments: {comment_count}")
        
        scraper2 = InstagramProfileScraper()
        
        search2_start = time.time()
        
        if scraper2.initialize():
            current_account = scraper2.scraper.session_manager.get_current_account()
            print(f"✅ Logged in with: {current_account['username']}")
            
            result2 = scraper2.search_by_location(location, post_count, comment_count)
            
            search2_time = time.time() - search2_start
            
            if result2 and "results" in result2 and result2["results"]:
                print(f"✅ Location search successful!")
                print(f"   Found {len(result2['results'])} posts")
                print(f"   Time: {search2_time:.2f} seconds")
                
                # Save results
                output_file2 = f"output/phase5_final_location_{int(time.time())}.json"
                with open(output_file2, 'w', encoding='utf-8') as f:
                    json.dump(result2, f, ensure_ascii=False, indent=2)
                
                test_results["location_search"] = {
                    "success": True,
                    "posts_found": len(result2["results"]),
                    "time": search2_time,
                    "output_file": output_file2
                }
                
                # Print first post as example
                if result2["results"]:
                    first_post = result2["results"][0]
                    print(f"   Example post: @{first_post.get('usernamePost', 'Unknown')}")
                    print(f"   Caption: {first_post.get('caption', 'No caption')[:100]}...")
                
            else:
                print(f"❌ Location search failed")
                test_results["location_search"] = {
                    "success": False,
                    "error": "No posts found",
                    "time": search2_time
                }
        else:
            print(f"❌ Failed to initialize scraper for location search")
            test_results["location_search"] = {
                "success": False,
                "error": "Initialization failed",
                "time": 0
            }
        
        # Close second scraper
        if scraper2.scraper:
            scraper2.scraper.close()
        
        test_results["total_test_time"] = time.time() - start_time
        
        # Generate final report
        print("\n" + "="*60)
        print("PHASE 5 FINAL TEST RESULTS")
        print("="*60)
        
        print(f"🔧 Mode: HEADLESS")
        print(f"🔑 Login Account: {test_results['login_account_used']}")
        print(f"⏱️  Total Time: {test_results['total_test_time']:.2f} seconds")
        
        print(f"\n📊 Test Results:")
        
        # Suspected Account Search Results
        suspected_result = test_results["suspected_account_search"]
        if suspected_result and suspected_result["success"]:
            print(f"  ✅ Suspected Account Search: SUCCESS")
            print(f"     Posts found: {suspected_result['posts_found']}")
            print(f"     Time: {suspected_result['time']:.2f}s")
            print(f"     Output: {suspected_result['output_file']}")
        else:
            print(f"  ❌ Suspected Account Search: FAILED")
            if suspected_result:
                print(f"     Error: {suspected_result.get('error', 'Unknown')}")
        
        # Location Search Results
        location_result = test_results["location_search"]
        if location_result and location_result["success"]:
            print(f"  ✅ Location Search: SUCCESS")
            print(f"     Posts found: {location_result['posts_found']}")
            print(f"     Time: {location_result['time']:.2f}s")
            print(f"     Output: {location_result['output_file']}")
        else:
            print(f"  ❌ Location Search: FAILED")
            if location_result:
                print(f"     Error: {location_result.get('error', 'Unknown')}")
        
        # Save test results
        results_file = f"output/phase5_final_test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Complete test results saved: {results_file}")
        
        # Determine overall success
        suspected_success = suspected_result and suspected_result["success"]
        location_success = location_result and location_result["success"]
        
        if suspected_success and location_success:
            print(f"\n🎉 PHASE 5 COMPLETE: Both search types working!")
            return True
        elif suspected_success or location_success:
            print(f"\n⚠️  PHASE 5 PARTIAL: One search type working")
            return True
        else:
            print(f"\n❌ PHASE 5 FAILED: Both search types failed")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during Phase 5 final test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        test_results["error"] = str(e)
        test_results["total_test_time"] = time.time() - start_time
        
        # Save error results
        error_file = f"output/phase5_final_test_error_{int(time.time())}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        return False
        
    finally:
        print("\nPhase 5 final test completed.")

if __name__ == "__main__":
    success = test_phase5_headless_real_accounts()
    if success:
        print("\n🏆 Phase 5 implementation successful!")
    else:
        print("\n💔 Phase 5 needs more work.")
