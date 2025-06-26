"""
Instagram Profile Scraper - Phase 5 Main File
Phase 5: Search by Location or Suspected Account

This is the main file to run Phase 5 logic, coordinating between
location search and suspected account search methods.
"""

import os
import sys
import json
import argparse
import time
from typing import Dict, Optional

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper


class Phase5InstagramScraper:
    """Phase 5 Instagram Scraper for location and suspected account search."""
    
    def __init__(self):
        self.scraper = None
        
    def run_location_search(self, location: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Run location-based search.
        
        Args:
            location: Location name to search for
            post_count: Number of posts to retrieve
            comment_count: Number of comments per post
            
        Returns:
            Dictionary with search results
        """
        try:
            # Initialize scraper
            self.scraper = InstagramProfileScraper()
            
            # Initialize the scraper (login, etc.)
            if not self.scraper.initialize():
                return {"error": "Failed to initialize scraper", "results": []}
            
            print(f"🔍 Starting location search for: {location}")
            print(f"📍 Target posts: {post_count}, Comments per post: {comment_count}")
            
            # Perform location search
            results = self.scraper.search_by_location(location, post_count, comment_count)
            
            # Save results
            output_file = self.scraper.save_phase5_results(results)
            
            print(f"✅ Location search completed!")
            print(f"📊 Results: {results.get('posts_extracted', 0)} posts extracted")
            print(f"💾 Results saved to: {output_file}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in location search: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "results": []}
        finally:
            if self.scraper:
                self.scraper.cleanup()
    
    def run_suspected_account_search(self, account_username: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Run suspected account search.
        
        Args:
            account_username: Username of suspected account
            post_count: Number of posts to retrieve
            comment_count: Number of comments per post
            
        Returns:
            Dictionary with search results
        """
        try:
            # Initialize scraper
            self.scraper = InstagramProfileScraper()
            
            # Initialize the scraper (login, etc.)
            if not self.scraper.initialize():
                return {"error": "Failed to initialize scraper", "results": []}
            
            print(f"🔍 Starting suspected account search for: @{account_username}")
            print(f"📍 Target posts: {post_count}, Comments per post: {comment_count}")
            
            # Perform suspected account search
            results = self.scraper.search_by_suspected_account(account_username, post_count, comment_count)
            
            # Save results
            output_file = self.scraper.save_phase5_results(results)
            
            print(f"✅ Suspected account search completed!")
            print(f"📊 Results: {results.get('posts_extracted', 0)} posts extracted")
            print(f"💾 Results saved to: {output_file}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in suspected account search: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "results": []}
        finally:
            if self.scraper:
                self.scraper.cleanup()
    
    def run_interactive_search(self):
        """Run interactive search mode."""
        print("🔍 Instagram Profile Scraper - Phase 5")
        print("=====================================")
        print("Search Options:")
        print("1. Search by Location")
        print("2. Search by Suspected Account")
        print("3. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    location = input("Enter location name: ").strip()
                    if not location:
                        print("❌ Location cannot be empty!")
                        continue
                    
                    post_count = self._get_positive_int("Number of posts (default 10): ", 10)
                    comment_count = self._get_positive_int("Comments per post (default 5): ", 5)
                    
                    results = self.run_location_search(location, post_count, comment_count)
                    self._display_results(results)
                    
                elif choice == "2":
                    account = input("Enter suspected account username (without @): ").strip()
                    if not account:
                        print("❌ Account username cannot be empty!")
                        continue
                    
                    post_count = self._get_positive_int("Number of posts (default 10): ", 10)
                    comment_count = self._get_positive_int("Comments per post (default 5): ", 5)
                    
                    results = self.run_suspected_account_search(account, post_count, comment_count)
                    self._display_results(results)
                    
                elif choice == "3":
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid choice! Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _get_positive_int(self, prompt: str, default: int) -> int:
        """Get a positive integer from user input."""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    return default
                
                num = int(value)
                if num > 0:
                    return num
                else:
                    print("❌ Please enter a positive number!")
            except ValueError:
                print("❌ Please enter a valid number!")
    
    def _display_results(self, results: Dict):
        """Display search results summary."""
        print("\n" + "="*50)
        print("📊 SEARCH RESULTS SUMMARY")
        print("="*50)
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"🔍 Search Type: {results.get('search_type', 'Unknown').replace('_', ' ').title()}")
        print(f"🎯 Search Target: {results.get('search_target', 'Unknown')}")
        print(f"📍 Posts Found: {results.get('total_posts_found', 0)}")
        print(f"✅ Posts Extracted: {results.get('posts_extracted', 0)}")
        print(f"⏰ Extraction Time: {results.get('extraction_time', 'Unknown')}")
        
        if results.get('results'):
            print(f"\n📋 Sample Posts:")
            for i, post in enumerate(results['results'][:3]):  # Show first 3 posts
                print(f"  {i+1}. {post.get('urlPost', 'No URL')}")
                print(f"     Username: {post.get('usernamePost', 'Unknown')}")
                print(f"     Caption: {post.get('caption', 'No caption')[:50]}...")
        
        print("="*50)


def main():
    """Main entry point for Phase 5 scraper."""
    parser = argparse.ArgumentParser(description="Instagram Profile Scraper - Phase 5")
    parser.add_argument("--mode", choices=["location", "account", "interactive"], 
                       default="interactive", help="Search mode")
    parser.add_argument("--target", help="Location name or account username")
    parser.add_argument("--posts", type=int, default=10, help="Number of posts to extract")
    parser.add_argument("--comments", type=int, default=5, help="Number of comments per post")
    
    args = parser.parse_args()
    
    phase5_scraper = Phase5InstagramScraper()
    
    try:
        if args.mode == "interactive":
            phase5_scraper.run_interactive_search()
        
        elif args.mode == "location":
            if not args.target:
                print("❌ Error: --target is required for location search")
                sys.exit(1)
            
            print(f"🔍 Running location search for: {args.target}")
            results = phase5_scraper.run_location_search(args.target, args.posts, args.comments)
            
            if "error" not in results:
                print(f"✅ Location search completed successfully!")
            else:
                print(f"❌ Location search failed: {results['error']}")
                sys.exit(1)
        
        elif args.mode == "account":
            if not args.target:
                print("❌ Error: --target is required for account search")
                sys.exit(1)
            
            print(f"🔍 Running suspected account search for: @{args.target}")
            results = phase5_scraper.run_suspected_account_search(args.target, args.posts, args.comments)
            
            if "error" not in results:
                print(f"✅ Suspected account search completed successfully!")
            else:
                print(f"❌ Suspected account search failed: {results['error']}")
                sys.exit(1)
    
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
