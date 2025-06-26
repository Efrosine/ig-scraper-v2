"""
Instagram Profile Scraper - Main Module
Phase 5: Search by Location or Suspected Account

This module serves as the main entry point for core functionality.
Enhanced with location and suspected account search capabilities.
"""

import json
import time
import sys
import os
from typing import Dict, List, Optional

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from scraper import InstagramScraper
from parser import InstagramPostParser
from data_cleaner import DataCleaner
from location_search import LocationSearcher
from suspected_account_search import SuspectedAccountSearcher
from output_logger import OutputLogger
from utils import setup_logging


class InstagramProfileScraper:
    """Main Instagram Profile Scraper class for Phase 5 with search capabilities."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.output_logger = OutputLogger()
        self.scraper = None
        self.parser = None
        self.data_cleaner = None
        self.location_searcher = None
        self.suspected_account_searcher = None
        self.session_data = {}
        
    def initialize(self) -> bool:
        """Initialize the scraper and attempt login."""
        try:
            self.logger.info("=== Instagram Profile Scraper - Phase 5 ===")
            self.logger.info("Initializing scraper with search capabilities...")
            
            # Create scraper instance
            self.scraper = InstagramScraper()
            
            # Create parser and data cleaner instances
            self.parser = InstagramPostParser()
            self.data_cleaner = DataCleaner()
            
            # Attempt login with backup support
            login_success = self.scraper.login_with_backup_support()
            
            if login_success:
                self.logger.info("Login successful - initializing search components...")
                
                # Initialize search components
                self.location_searcher = LocationSearcher(self.scraper.driver, self.logger)
                self.suspected_account_searcher = SuspectedAccountSearcher(self.scraper.driver, self.logger)
                
                # Verify search capabilities
                location_capability = self.location_searcher.verify_location_search_capability()
                account_capability = self.suspected_account_searcher.verify_account_search_capability()
                
                current_account = self.scraper.session_manager.get_current_account()
                self.session_data = {
                    "current_account": current_account['username'],
                    "login_time": time.time(),
                    "total_accounts": self.scraper.session_manager.get_account_count(),
                    "remaining_accounts": self.scraper.session_manager.get_remaining_accounts(),
                    "phase": "5",
                    "location_search_available": location_capability,
                    "account_search_available": account_capability,
                    "features": ["location_search", "suspected_account_search", "enhanced_logging", "data_cleaning", "quality_scoring"]
                }
                
                self.logger.info("Phase 5 initialization completed successfully")
                self.logger.info(f"Location search available: {location_capability}")
                self.logger.info(f"Account search available: {account_capability}")
                return True
            else:
                self.logger.error("Failed to initialize scraper - login unsuccessful")
                return False
                
        except Exception as e:
            self.logger.error(f"Critical error during initialization: {str(e)}")
            return False
    
    def get_session_info(self) -> Dict:
        """Get current session information."""
        return {
            "session_data": self.session_data,
            "status": "active" if self.scraper else "inactive",
            "timestamp": time.time()
        }
    
    def test_basic_navigation(self) -> bool:
        """Test basic navigation to verify the scraper is working."""
        try:
            if not self.scraper or not self.scraper.driver:
                self.logger.error("Scraper not initialized")
                return False
            
            self.logger.info("Testing basic navigation...")
            
            # Navigate to Instagram home
            self.scraper.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Take a screenshot for verification
            self.scraper.take_screenshot("phase1_navigation_test.png")
            
            current_url = self.scraper.driver.current_url
            self.logger.info(f"Current URL: {current_url}")
            
            # Check if we're still logged in
            if "instagram.com/accounts/login" in current_url:
                self.logger.warning("Redirected to login page - session may have expired")
                return False
            
            # Check for auth platform code entry - indicates login failure
            if "instagram.com/auth_platform/codeentry" in current_url:
                self.logger.error("Navigation test failed - at code entry page (login failed)")
                return False
            
            # Check for other login-related issues
            failed_login_patterns = ["challenge", "two_factor", "checkpoint", "suspend", "confirm"]
            for pattern in failed_login_patterns:
                if pattern in current_url.lower():
                    self.logger.error(f"Navigation test failed - suspicious URL: {current_url}")
                    return False
                return False
            
            self.logger.info("Basic navigation test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during navigation test: {str(e)}")
            return False
    
    def save_phase1_results(self) -> str:
        """Save Phase 1 results to JSON file."""
        try:
            timestamp = int(time.time())
            results = {
                "phase": 1,
                "title": "Foundation, Login & Backup Accounts",
                "timestamp": timestamp,
                "session_info": self.get_session_info(),
                "status": "completed",
                "features_implemented": [
                    "Selenium WebDriver setup",
                    "Instagram login automation",
                    "Session persistence with cookies",
                    "Backup account support",
                    "Rate limiting",
                    "Error handling and logging"
                ]
            }
            
            # Save main results
            output_file = os.path.join("output", "phase1_results.json")
            os.makedirs("output", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save backup
            backup_file = os.path.join("output", f"backup_phase1_{timestamp}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Phase 1 results saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error saving Phase 1 results: {str(e)}")
            return ""
    
    def run_phase1_complete(self) -> bool:
        """Run complete Phase 1 workflow."""
        try:
            self.logger.info("=== Starting Phase 1: Foundation, Login & Backup Accounts ===")
            
            # Step 1: Initialize scraper and login
            if not self.initialize():
                return False
            
            # Step 2: Test basic functionality
            if not self.test_basic_navigation():
                self.logger.warning("Basic navigation test failed, but login was successful")
            
            # Step 3: Save results
            output_file = self.save_phase1_results()
            if not output_file:
                self.logger.error("Failed to save Phase 1 results")
                return False
            
            self.logger.info("=== Phase 1 completed successfully ===")
            self.logger.info(f"Session active with account: {self.session_data.get('current_account', 'Unknown')}")
            self.logger.info(f"Remaining backup accounts: {self.session_data.get('remaining_accounts', 0)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Critical error during Phase 1 execution: {str(e)}")
            return False
        finally:
            # Keep the session active for next phases
            pass
    
    def extract_profile(self, username: str) -> Dict:
        """
        Extract profile data for a specific username.
        
        Args:
            username (str): Instagram username to extract data from
            
        Returns:
            Dict: Profile extraction results
        """
        try:
            if not self.scraper or not self.scraper.driver:
                self.logger.error("Scraper not initialized")
                return {"success": False, "error": "Scraper not initialized"}
            
            self.logger.info(f"=== Phase 2: Profile Extraction for @{username} ===")
            
            # Navigate to profile
            navigation_success = self.scraper.navigate_to_profile(username)
            if not navigation_success:
                return {
                    "success": False,
                    "error": f"Failed to navigate to profile @{username}",
                    "username": username
                }
            
            # Take screenshot after navigation
            self.scraper.take_screenshot(f"phase2_profile_{username}.png")
            
            # Extract profile data
            profile_data = self.scraper.extract_profile_data(username)
            
            # Create Phase 2 JSON structure
            phase2_results = {
                "success": True,
                "phase": "Phase 2 - Profile Extraction",
                "extraction_timestamp": time.time(),
                "profile_data": profile_data,
                "session_info": {
                    "current_account": self.session_data.get("current_account", "unknown"),
                    "extraction_duration": time.time() - profile_data.get("extraction_timestamp", time.time())
                }
            }
            
            self.logger.info(f"Profile extraction completed for @{username}")
            return phase2_results
            
        except Exception as e:
            self.logger.error(f"Error during profile extraction for @{username}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "username": username,
                "phase": "Phase 2 - Profile Extraction"
            }
    
    def save_phase2_results(self, results: Dict, username: str) -> str:
        """
        Save Phase 2 results to JSON file.
        
        Args:
            results (Dict): Phase 2 extraction results
            username (str): Username that was extracted
            
        Returns:
            str: Path to saved results file
        """
        try:
            # Create output directory
            os.makedirs("output", exist_ok=True)
            
            # Generate filename
            timestamp = int(time.time())
            filename = f"phase2_profile_{username}_{timestamp}.json"
            filepath = os.path.join("output", filename)
            
            # Save results
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Phase 2 results saved to: {filepath}")
            
            # Also save as latest results
            latest_filepath = os.path.join("output", "phase2_latest_results.json")
            with open(latest_filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving Phase 2 results: {str(e)}")
            return ""

    def scrape_profile_posts(self, username: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Scrape posts from Instagram profile - Phase 3 functionality.
        
        Args:
            username: Instagram username to scrape
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            
        Returns:
            Dictionary containing scraped posts data
        """
        try:
            if not self.scraper:
                raise Exception("Scraper not initialized. Call initialize() first.")
                
            self.logger.info(f"=== Phase 3: Post Scraping ===")
            self.logger.info(f"Scraping posts from @{username}")
            
            # Use scraper's post scraping functionality
            result = self.scraper.scrape_posts(username, post_count, comment_count)
            
            # Add metadata
            result.update({
                "phase": 3,
                "scraper_version": "1.0",
                "extraction_settings": {
                    "post_count": post_count,
                    "comment_count": comment_count,
                    "username": username
                }
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in profile post scraping: {str(e)}")
            return {
                "phase": 3,
                "error": str(e),
                "username": username,
                "results": []
            }
    
    def save_phase3_results(self, results: Dict, username: str) -> str:
        """Save Phase 3 post scraping results to JSON file."""
        try:
            timestamp = int(time.time())
            
            # Prepare results with metadata
            output_data = {
                "phase": 3,
                "title": "Post Scraping",
                "timestamp": timestamp,
                "target_username": username,
                "scraping_results": results,
                "status": "completed" if "error" not in results else "error"
            }
            
            # Save main results
            output_file = os.path.join("output", f"phase3_posts_{username}_{timestamp}.json")
            os.makedirs("output", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Also save in standard format for compatibility
            latest_file = os.path.join("output", "phase3_latest_results.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Phase 3 results saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error saving Phase 3 results: {str(e)}")
            return ""
    
    def scrape_posts_enhanced(self, username: str, post_count: int = 10, comment_count: int = 5, min_quality: float = 0.5) -> Dict:
        """
        Phase 4: Enhanced post scraping with advanced parsing, cleaning, and quality scoring.
        
        Args:
            username: Instagram username to scrape
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            min_quality: Minimum quality score for posts (0.0-1.0)
            
        Returns:
            Dictionary containing enhanced scraped posts with cleaning stats
        """
        try:
            if not self.scraper or not self.parser or not self.data_cleaner:
                raise Exception("Scraper not properly initialized for Phase 4")
            
            self.logger.info(f"=== Phase 4: Enhanced Post Scraping for @{username} ===")
            self.logger.info(f"Extracting {post_count} posts with {comment_count} comments each")
            self.logger.info(f"Minimum quality threshold: {min_quality}")
            
            # Extract posts using enhanced parser
            posts_data = self.parser.extract_profile_posts(
                self.scraper.driver, 
                username, 
                post_count, 
                comment_count
            )
            
            raw_posts = posts_data.get("results", [])
            self.logger.info(f"Raw extraction completed: {len(raw_posts)} posts")
            
            if not raw_posts:
                self.logger.warning("No posts extracted")
                return {
                    "phase": 4,
                    "username": username,
                    "error": "No posts found or extracted",
                    "results": []
                }
            
            # Apply data cleaning and enhancement
            self.logger.info("Applying data cleaning and quality scoring...")
            cleaned_posts = []
            
            for i, post in enumerate(raw_posts):
                try:
                    cleaned_post = self.data_cleaner.clean_post_data(post)
                    cleaned_posts.append(cleaned_post)
                    
                    quality_score = cleaned_post.get("quality_score", 0.0)
                    self.logger.debug(f"Post {i+1} quality score: {quality_score:.2f}")
                    
                except Exception as e:
                    self.logger.error(f"Error cleaning post {i+1}: {str(e)}")
                    # Keep original data if cleaning fails
                    cleaned_posts.append(post)
            
            # Filter by quality if requested
            if min_quality > 0.0:
                filtered_posts = self.data_cleaner.filter_by_quality(cleaned_posts, min_quality)
                self.logger.info(f"Quality filtering: {len(cleaned_posts)} -> {len(filtered_posts)} posts")
            else:
                filtered_posts = cleaned_posts
            
            # Generate cleaning statistics
            cleaning_stats = self.data_cleaner.get_cleaning_stats(raw_posts, filtered_posts)
            
            # Take screenshot for verification
            try:
                self.scraper.take_screenshot(f"phase4_posts_{username}_{int(time.time())}.png")
            except:
                pass
            
            # Prepare enhanced results
            result = {
                "phase": 4,
                "title": "Enhanced Post Scraping with Data Cleaning",
                "username": username,
                "extraction_time": posts_data.get("extraction_time"),
                "total_posts_extracted": len(raw_posts),
                "posts_after_cleaning": len(filtered_posts),
                "requested_posts": post_count,
                "requested_comments_per_post": comment_count,
                "min_quality_threshold": min_quality,
                "cleaning_stats": cleaning_stats,
                "features_applied": [
                    "advanced_beautifulsoup_parsing",
                    "data_cleaning_normalization", 
                    "quality_scoring",
                    "metadata_extraction",
                    "emoji_normalization",
                    "text_cleaning"
                ],
                "results": filtered_posts,
                "session_info": {
                    "current_account": self.session_data.get("current_account"),
                    "post_count": post_count,
                    "comment_count": comment_count,
                    "username": username,
                    "phase": 4
                }
            }
            
            self.logger.info(f"Phase 4 enhanced post scraping completed for @{username}")
            self.logger.info(f"Results: {len(filtered_posts)} quality posts with avg score {cleaning_stats.get('avg_quality_score', 0):.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in Phase 4 enhanced post scraping: {str(e)}")
            return {
                "phase": 4,
                "error": str(e),
                "username": username,
                "results": []
            }
    
    def save_phase4_results(self, results: Dict, username: str) -> str:
        """Save Phase 4 enhanced results to JSON file."""
        try:
            timestamp = int(time.time())
            
            # Prepare results with enhanced metadata
            output_data = {
                "phase": 4,
                "title": "Enhanced Post Scraping with Data Cleaning",
                "timestamp": timestamp,
                "target_username": username,
                "scraping_results": results,
                "status": "completed" if "error" not in results else "error",
                "features": [
                    "advanced_parsing",
                    "data_cleaning", 
                    "quality_scoring",
                    "metadata_extraction"
                ]
            }
            
            # Save main results
            output_file = os.path.join("output", f"phase4_posts_{username}_{timestamp}.json")
            os.makedirs("output", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Also save in standard format for compatibility
            latest_file = os.path.join("output", "phase4_latest_results.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Phase 4 enhanced results saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error saving Phase 4 results: {str(e)}")
            return ""
    
    def search_by_location(self, location: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Phase 5: Search Instagram posts by location.
        
        Args:
            location: Location name to search for
            post_count: Number of posts to retrieve
            comment_count: Number of comments per post
            
        Returns:
            Dictionary with search results
        """
        try:
            self.logger.info(f"=== Phase 5: Location Search ===")
            self.logger.info(f"Searching for posts in location: {location}")
            
            # Initialize search components if not already done
            if not self.location_searcher:
                self.location_searcher = LocationSearcher(self.scraper.driver, self.logger)
            
            # Start session logging
            session_info = self.output_logger.log_session_start(
                search_type="location",
                search_target=location,
                parameters={
                    "post_count": post_count,
                    "comment_count": comment_count,
                    "location": location
                }
            )
            
            # Perform location search
            self.output_logger.log_search_operation(
                "Location Search Initialization",
                {"location": location, "target_posts": post_count}
            )
            
            post_links = self.location_searcher.search_by_location(location, post_count)
            
            if not post_links:
                self.logger.warning(f"No posts found for location: {location}")
                return self._create_empty_search_result("location", location, "No posts found")
            
            self.logger.info(f"Found {len(post_links)} posts for location: {location}")
            
            # Extract detailed post data
            extracted_posts = []
            for i, post_data in enumerate(post_links):
                try:
                    self.logger.info(f"Extracting post {i+1}/{len(post_links)}: {post_data['url']}")
                    
                    # Navigate to post
                    self.scraper.driver.get(post_data['url'])
                    time.sleep(3)
                    
                    # Extract post details
                    post_details = self.parser.extract_post_data(
                        self.scraper.driver.page_source,
                        post_data['url']
                    )
                    
                    if post_details:
                        # Clean and enhance the data
                        cleaned_post = self.data_cleaner.clean_post_data(post_details)
                        
                        # Add search metadata
                        cleaned_post.update({
                            'search_type': 'location',
                            'search_target': location,
                            'found_via': post_data.get('found_via', 'location_page')
                        })
                        
                        # Extract comments if requested
                        if comment_count > 0:
                            comments = self.parser.extract_comments(
                                self.scraper.driver.page_source,
                                comment_count
                            )
                            cleaned_post['comments'] = comments
                        
                        extracted_posts.append(cleaned_post)
                        
                        self.output_logger.log_post_extraction(
                            post_data['url'],
                            {"success": True, "quality_score": cleaned_post.get("quality_score", 0)}
                        )
                    else:
                        self.logger.warning(f"Failed to extract data from post: {post_data['url']}")
                        
                except Exception as e:
                    self.logger.error(f"Error extracting post {i+1}: {str(e)}")
                    self.output_logger.log_error(
                        "PostExtractionError",
                        str(e),
                        {"post_url": post_data.get('url', 'Unknown'), "post_index": i+1}
                    )
                    continue
            
            # End session logging
            session_info = self.output_logger.log_session_end(
                session_info, len(extracted_posts), len(extracted_posts) > 0
            )
            
            # Create standardized result
            result = {
                "phase": 5,
                "search_type": "location",
                "search_target": location,
                "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": self.output_logger.get_session_id(),
                "total_posts_found": len(post_links),
                "posts_extracted": len(extracted_posts),
                "requested_posts": post_count,
                "requested_comments_per_post": comment_count,
                "search_algorithm": "location_based",
                "results": extracted_posts,
                "session_info": session_info
            }
            
            self.logger.info(f"Location search completed: {len(extracted_posts)} posts extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in location search: {str(e)}")
            self.output_logger.log_error("LocationSearchError", str(e), {"location": location})
            return self._create_empty_search_result("location", location, str(e))
    
    def search_by_suspected_account(self, account_username: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Phase 5: Search Instagram posts by suspected account.
        
        Args:
            account_username: Username of suspected account
            post_count: Number of posts to retrieve
            comment_count: Number of comments per post
            
        Returns:
            Dictionary with search results
        """
        try:
            self.logger.info(f"=== Phase 5: Suspected Account Search ===")
            self.logger.info(f"Searching posts from suspected account: {account_username}")
            
            # Initialize search components if not already done
            if not self.suspected_account_searcher:
                self.suspected_account_searcher = SuspectedAccountSearcher(self.scraper.driver, self.logger)
            
            # Start session logging
            session_info = self.output_logger.log_session_start(
                search_type="suspected_account",
                search_target=account_username,
                parameters={
                    "post_count": post_count,
                    "comment_count": comment_count,
                    "account_username": account_username
                }
            )
            
            # Get account info first
            account_info = self.suspected_account_searcher.get_account_info(account_username)
            if not account_info:
                self.logger.warning(f"Account not accessible: {account_username}")
                return self._create_empty_search_result("suspected_account", account_username, "Account not accessible")
            
            self.output_logger.log_search_operation(
                "Account Information Retrieved",
                {"account": account_username, "accessible": account_info.get('is_accessible', False)}
            )
            
            # Perform suspected account search
            post_links = self.suspected_account_searcher.search_by_suspected_account(account_username, post_count)
            
            if not post_links:
                self.logger.warning(f"No posts found for account: {account_username}")
                return self._create_empty_search_result("suspected_account", account_username, "No posts found")
            
            self.logger.info(f"Found {len(post_links)} posts for account: {account_username}")
            
            # Extract detailed post data
            extracted_posts = []
            for i, post_data in enumerate(post_links):
                try:
                    self.logger.info(f"Extracting post {i+1}/{len(post_links)}: {post_data['url']}")
                    
                    # Navigate to post
                    self.scraper.driver.get(post_data['url'])
                    time.sleep(3)
                    
                    # Extract post details
                    post_details = self.parser.extract_post_data(
                        self.scraper.driver.page_source,
                        post_data['url']
                    )
                    
                    if post_details:
                        # Clean and enhance the data
                        cleaned_post = self.data_cleaner.clean_post_data(post_details)
                        
                        # Add search metadata
                        cleaned_post.update({
                            'search_type': 'suspected_account',
                            'search_target': account_username,
                            'found_via': post_data.get('found_via', 'profile_page'),
                            'account_info': account_info
                        })
                        
                        # Extract comments if requested
                        if comment_count > 0:
                            comments = self.parser.extract_comments(
                                self.scraper.driver.page_source,
                                comment_count
                            )
                            cleaned_post['comments'] = comments
                        
                        extracted_posts.append(cleaned_post)
                        
                        self.output_logger.log_post_extraction(
                            post_data['url'],
                            {"success": True, "quality_score": cleaned_post.get("quality_score", 0)}
                        )
                    else:
                        self.logger.warning(f"Failed to extract data from post: {post_data['url']}")
                        
                except Exception as e:
                    self.logger.error(f"Error extracting post {i+1}: {str(e)}")
                    self.output_logger.log_error(
                        "PostExtractionError",
                        str(e),
                        {"post_url": post_data.get('url', 'Unknown'), "post_index": i+1}
                    )
                    continue
            
            # End session logging
            session_info = self.output_logger.log_session_end(
                session_info, len(extracted_posts), len(extracted_posts) > 0
            )
            
            # Create standardized result
            result = {
                "phase": 5,
                "search_type": "suspected_account",
                "search_target": account_username,
                "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": self.output_logger.get_session_id(),
                "total_posts_found": len(post_links),
                "posts_extracted": len(extracted_posts),
                "requested_posts": post_count,
                "requested_comments_per_post": comment_count,
                "search_algorithm": "suspected_account_based",
                "account_info": account_info,
                "results": extracted_posts,
                "session_info": session_info
            }
            
            self.logger.info(f"Suspected account search completed: {len(extracted_posts)} posts extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in suspected account search: {str(e)}")
            self.output_logger.log_error("SuspectedAccountSearchError", str(e), {"account": account_username})
            return self._create_empty_search_result("suspected_account", account_username, str(e))
    
    def run_search_operation(self, search_type: str, search_target: str, post_count: int = 10, comment_count: int = 5) -> Dict:
        """
        Phase 5: Run search operation based on type.
        
        Args:
            search_type: Either 'location' or 'suspected_account'
            search_target: Location name or account username
            post_count: Number of posts to retrieve
            comment_count: Number of comments per post
            
        Returns:
            Dictionary with search results
        """
        try:
            if search_type == "location":
                return self.search_by_location(search_target, post_count, comment_count)
            elif search_type == "suspected_account":
                return self.search_by_suspected_account(search_target, post_count, comment_count)
            else:
                raise ValueError(f"Invalid search type: {search_type}. Must be 'location' or 'suspected_account'")
                
        except Exception as e:
            self.logger.error(f"Error in search operation: {str(e)}")
            return self._create_empty_search_result(search_type, search_target, str(e))
    
    def _create_empty_search_result(self, search_type: str, search_target: str, error_message: str) -> Dict:
        """Create an empty search result with error information."""
        return {
            "phase": 5,
            "search_type": search_type,
            "search_target": search_target,
            "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.output_logger.get_session_id(),
            "total_posts_found": 0,
            "posts_extracted": 0,
            "error": error_message,
            "results": []
        }
    
    def save_phase5_results(self, results: Dict) -> str:
        """Save Phase 5 search results to JSON file."""
        try:
            timestamp = int(time.time())
            search_type = results.get("search_type", "unknown")
            search_target = results.get("search_target", "unknown")
            
            # Prepare results with enhanced metadata
            output_data = {
                "phase": 5,
                "title": f"Search by {search_type.replace('_', ' ').title()}",
                "timestamp": timestamp,
                "search_type": search_type,
                "search_target": search_target,
                "scraping_results": results,
                "status": "completed" if "error" not in results else "error",
                "features": [
                    "location_search" if search_type == "location" else "suspected_account_search",
                    "enhanced_logging",
                    "data_cleaning",
                    "quality_scoring"
                ]
            }
            
            # Save main results
            output_file = os.path.join("output", f"phase5_{search_type}_{search_target}_{timestamp}.json")
            os.makedirs("output", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Also save in standard format for compatibility
            latest_file = os.path.join("output", "phase5_latest_results.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Phase 5 search results saved to {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error saving Phase 5 results: {str(e)}")
            return ""

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.scraper:
                self.scraper.close()
                self.logger.info("Scraper resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


if __name__ == "__main__":
    # This allows the main module to be run directly for testing
    with InstagramProfileScraper() as scraper:
        success = scraper.initialize()
        if success:
            print("Phase 5 initialized successfully!")
            print("Ready for location or suspected account search")
        else:
            print("Phase 5 initialization failed.")
            sys.exit(1)
