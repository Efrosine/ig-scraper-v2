#!/usr/bin/env python3
"""
Test the API with actual scraping
"""

import requests
import json
import sys
import os

def test_api_scraping():
    """Test the API with real scraping"""
    print("=== Testing API with Real Scraping ===")
    
    base_url = "http://localhost:5000"
    
    # Test health first
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed - is the server running?")
            print("Start the server with: python 'phase files/phase7_scraper.py'")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Start the server with: python 'phase files/phase7_scraper.py'")
        return
    
    # Test scraping
    test_data = {
        "suspected_account": "malangraya_info",
        "post_count": 2,
        "comment_count": 2
    }
    
    print(f"Sending scraping request: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes for scraping
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Scraping Successful!")
            print(f"Posts extracted: {len(data.get('results', []))}")
            print(f"Status: {data.get('status', 'unknown')}")
            
            # Show first result
            results = data.get('results', [])
            if results:
                first_post = results[0]
                print(f"\nFirst Post:")
                print(f"  Username: {first_post.get('usernamePost', 'N/A')}")
                print(f"  URL: {first_post.get('urlPost', 'N/A')}")
                print(f"  Caption: {first_post.get('caption', 'N/A')[:100]}...")
                print(f"  Comments: {len(first_post.get('comments', {}))}")
            
            print("\n✅ Phase 7 API is working correctly!")
            
        else:
            try:
                error_data = response.json()
                print(f"❌ API Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"❌ HTTP Error: {response.status_code}")
                print(response.text[:500])
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out - scraping may take longer")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_scraping()
