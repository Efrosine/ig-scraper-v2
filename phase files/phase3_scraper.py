"""
Instagram Profile Scraper - Phase 3: Post Scraping
Main file to run post scraping functionality

This module serves as the main entry point for Phase 3 post scraping.
Extracts post data (username, URL, release date, caption, comments) with configurable counts.
"""

import json
import time
import sys
import os
from typing import Dict, List

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper
from utils import setup_logging


class Phase3InstagramScraper:
    """Phase 3 Instagram Post Scraper - Main execution class."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scraper = None
        
    def run_phase3_complete(self, username: str = "malangraya_info", post_count: int = 10, comment_count: int = 5) -> bool:
        """
        Run complete Phase 3 workflow: post scraping.
        
        Args:
            username: Instagram username to scrape posts from
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            
        Returns:
            bool: Success status
        """
        try:
            self.logger.info("=== Starting Phase 3: Post Scraping ===")
            self.logger.info(f"Target: @{username}")
            self.logger.info(f"Posts to extract: {post_count}")
            self.logger.info(f"Comments per post: {comment_count}")
            
            # Initialize the main scraper
            self.scraper = InstagramProfileScraper()
            
            # Step 1: Initialize and login (from Phase 1)
            self.logger.info("Step 1: Initializing scraper and login...")
            if not self.scraper.initialize():
                self.logger.error("Failed to initialize scraper")
                return False
            
            self.logger.info("Login successful, proceeding to post scraping...")
            
            # Step 2: Extract profile first (Phase 2 functionality)
            # self.logger.info("Step 2: Extracting profile information...")
            # profile_results = self.scraper.extract_profile(username)
            # if not profile_results.get("success", False):
            #     self.logger.warning(f"Profile extraction failed, but continuing with post scraping...")
            # else:
            #     self.logger.info("Profile extraction completed successfully")
            
            # Step 3: Scrape posts (Phase 3 core functionality)
            self.logger.info("Step 3: Starting post scraping...")
            post_results = self.scraper.scrape_profile_posts(username, post_count, comment_count)
            
            if "error" in post_results:
                self.logger.error(f"Post scraping failed: {post_results['error']}")
                return False
            
            self.logger.info(f"Successfully scraped {len(post_results.get('results', []))} posts")
            
            # Step 4: Save results
            self.logger.info("Step 4: Saving Phase 3 results...")
            output_file = self.scraper.save_phase3_results(post_results, username)
            if not output_file:
                self.logger.error("Failed to save Phase 3 results")
                return False
            
            # Step 5: Display summary
            self.display_scraping_summary(post_results, username, output_file)
            
            self.logger.info("=== Phase 3 completed successfully ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Critical error during Phase 3 execution: {str(e)}")
            return False
        finally:
            if self.scraper:
                # Keep browser open for inspection
                self.logger.info("Phase 3 completed. Browser session will remain open for inspection.")
                print("\n" + "="*60)
                print("Phase 3 Post Scraping completed!")
                print("Browser window will remain open for inspection.")
                print("Press Enter to close and cleanup...")
                print("="*60)
                input()  # Wait for user input before cleanup
                self.scraper.cleanup()
    
    def display_scraping_summary(self, results: Dict, username: str, output_file: str):
        """Display a summary of the scraping results."""
        try:
            print("\n" + "="*60)
            print("PHASE 3 POST SCRAPING SUMMARY")
            print("="*60)
            print(f"Target Username: @{username}")
            print(f"Results saved to: {output_file}")
            
            if "results" in results and results["results"]:
                print(f"Successfully scraped: {len(results['results'])} posts")
                print("\nSample post data:")
                
                # Display first post as sample
                first_post = results["results"][0]
                print(f"  - Username: {first_post.get('usernamePost', 'N/A')}")
                print(f"  - URL: {first_post.get('urlPost', 'N/A')}")
                print(f"  - Release Date: {first_post.get('releaseDate', 'N/A')}")
                print(f"  - Caption: {first_post.get('caption', 'N/A')[:100]}...")
                print(f"  - Comments: {len(first_post.get('comments', {}))}")
                
            else:
                print("No posts were extracted")
                
            if "error" in results:
                print(f"Errors encountered: {results['error']}")
                
            print("="*60)
            
        except Exception as e:
            self.logger.error(f"Error displaying summary: {str(e)}")
    
    def run_interactive_mode(self):
        """Run Phase 3 in interactive mode with user input."""
        try:
            print("\n" + "="*60)
            print("INSTAGRAM POST SCRAPER - PHASE 3")
            print("Interactive Mode")
            print("="*60)
            
            # Get user input
            username = input("Enter Instagram username to scrape (default: malangraya_info): ").strip()
            if not username:
                username = "malangraya_info"
            
            try:
                post_count = int(input("Enter number of posts to scrape (default: 10): ") or "10")
                comment_count = int(input("Enter number of comments per post (default: 5): ") or "5")
            except ValueError:
                print("Invalid input. Using default values.")
                post_count = 10
                comment_count = 5
            
            print(f"\nStarting scraping for @{username}...")
            print(f"Posts: {post_count}, Comments per post: {comment_count}")
            print("-" * 60)
            
            # Run the scraping
            success = self.run_phase3_complete(username, post_count, comment_count)
            
            if success:
                print("\n✅ Phase 3 completed successfully!")
            else:
                print("\n❌ Phase 3 failed. Check logs for details.")
                
            return success
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return False
        except Exception as e:
            print(f"\nError in interactive mode: {str(e)}")
            return False


def main():
    """Main entry point for Phase 3 scraper."""
    try:
        scraper = Phase3InstagramScraper()
        
        # Check if running with command line arguments
        if len(sys.argv) > 1:
            username = sys.argv[1] if len(sys.argv) > 1 else "malangraya_info"
            post_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            comment_count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            
            print(f"Running Phase 3 with: @{username}, {post_count} posts, {comment_count} comments")
            success = scraper.run_phase3_complete(username, post_count, comment_count)
        else:
            # Run interactive mode
            success = scraper.run_interactive_mode()
        
        if success:
            print("\nPhase 3 Post Scraping completed successfully!")
            sys.exit(0)
        else:
            print("\nPhase 3 Post Scraping failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
