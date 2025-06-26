"""
Instagram Profile Scraper - Main Module
Phase 1: Foundation, Login & Backup Accounts

This module serves as the main entry point for core functionality.
"""

import json
import time
import sys
import os
from typing import Dict, List, Optional

# Selenium imports for web scraping
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from scraper import InstagramScraper
from utils import setup_logging


class InstagramProfileScraper:
    """Main Instagram Profile Scraper class for Phase 1."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scraper = None
        self.session_data = {}
        
    def initialize(self) -> bool:
        """Initialize the scraper and attempt login."""
        try:
            self.logger.info("=== Instagram Profile Scraper - Phase 1 ===")
            self.logger.info("Initializing scraper with backup account support...")
            
            # Create scraper instance
            self.scraper = InstagramScraper()
            
            # Attempt login with backup support
            login_success = self.scraper.login_with_backup_support()
            
            if login_success:
                self.logger.info("Scraper initialized successfully")
                current_account = self.scraper.session_manager.get_current_account()
                self.session_data = {
                    "current_account": current_account['username'],
                    "login_time": time.time(),
                    "total_accounts": self.scraper.session_manager.get_account_count(),
                    "remaining_accounts": self.scraper.session_manager.get_remaining_accounts()
                }
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

    def scrape_profile(self, username: str) -> Optional[Dict]:
        """
        Navigate to and scrape basic profile information.
        
        Args:
            username: Instagram username to scrape
            
        Returns:
            Dictionary containing profile information or None if failed
        """
        try:
            if not self.scraper:
                self.logger.error("Scraper not initialized")
                return None
            
            self.logger.info(f"Navigating to profile: {username}")
            
            # Use scraper's navigation method
            navigation_success = self.scraper.navigate_to_profile(username)
            if not navigation_success:
                return {"username": username, "error": "Failed to navigate to profile"}
            
            # Extract basic profile info
            try:
                profile_data = {
                    "username": username,
                    "profile_url": f"https://www.instagram.com/{username}/",
                    "posts_count": "0",
                    "followers_count": "0",
                    "following_count": "0",
                    "bio": "",
                    "full_name": ""
                }
                
                # Try to get posts count
                posts_link = self.scraper.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
                if posts_link:
                    profile_data["has_posts"] = True
                    profile_data["posts_count"] = str(len(posts_link))
                else:
                    profile_data["has_posts"] = False
                
                # Try to get display name
                try:
                    name_element = self.scraper.driver.find_element(By.CSS_SELECTOR, "h1, h2")
                    if name_element:
                        profile_data["full_name"] = name_element.text.strip()
                except:
                    pass
                
                self.logger.info(f"Profile data extracted for {username}")
                return profile_data
                
            except Exception as e:
                self.logger.error(f"Error extracting profile data: {str(e)}")
                return {"username": username, "profile_url": f"https://www.instagram.com/{username}/", "error": str(e)}
                return profile_data
                
            except Exception as e:
                self.logger.error(f"Error extracting profile data: {str(e)}")
                return {"username": username, "profile_url": profile_url, "error": str(e)}
                
        except Exception as e:
            self.logger.error(f"Error navigating to profile {username}: {str(e)}")
            return None
    
    def scrape_posts(self, post_count: int = 10, comment_count: int = 5) -> List[Dict]:
        """
        Extract posts from current profile page.
        
        Args:
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            
        Returns:
            List of post data dictionaries
        """
        try:
            if not self.scraper:
                self.logger.error("Scraper not initialized")
                return []
            
            # Import parser
            from parser import InstagramPostParser
            
            # Create parser instance
            parser = InstagramPostParser()
            
            # Extract posts
            posts_data = parser.extract_post_data(
                self.scraper.driver, 
                post_count=post_count, 
                comment_count=comment_count
            )
            
            return posts_data
            
        except Exception as e:
            self.logger.error(f"Error extracting posts: {str(e)}")
            return []
