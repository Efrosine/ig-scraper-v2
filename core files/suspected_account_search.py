"""
Instagram Profile Scraper - Suspected Account Search Module
Phase 5: Search by Suspected Account

This module implements suspected account search functionality with its specific algorithm.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SuspectedAccountSearcher:
    """Handles suspected account Instagram search functionality."""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait_timeout = 10
        
    def search_by_suspected_account(self, account_username: str, post_count: int = 10) -> List[Dict]:
        """
        Search Instagram posts by suspected account using account-specific algorithm.
        
        Args:
            account_username: Username of suspected account to search
            post_count: Number of posts to retrieve
            
        Returns:
            List of post URLs found for the suspected account
        """
        try:
            self.logger.info(f"Starting suspected account search for: {account_username}")
            
            # Navigate directly to the suspected account profile
            profile_url = f"https://www.instagram.com/{account_username}/"
            self.driver.get(profile_url)
            time.sleep(5)
            
            # Check if profile exists and is accessible
            if self._is_profile_accessible():
                return self._collect_account_posts(account_username, post_count)
            else:
                self.logger.warning(f"Profile not accessible or doesn't exist: {account_username}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in suspected account search: {str(e)}")
            return []
    
    def _is_profile_accessible(self) -> bool:
        """
        Check if the current profile page is accessible.
        
        Returns:
            True if profile is accessible, False otherwise
        """
        try:
            # Check for profile indicators
            profile_indicators = [
                "//main[@role='main']",
                "//article",
                "//header//h2",  # Profile name
                "//div[contains(@class, 'post') or contains(@data-testid, 'post')]"
            ]
            
            for indicator in profile_indicators:
                element = self._wait_for_element(By.XPATH, indicator, timeout=5)
                if element:
                    self.logger.debug(f"Profile accessibility confirmed with: {indicator}")
                    return True
            
            # Check for error indicators
            error_indicators = [
                "//span[contains(text(), 'Sorry, this page') or contains(text(), 'Page Not Found')]",
                "//h2[contains(text(), 'This account is private')]"
            ]
            
            for error_indicator in error_indicators:
                element = self._wait_for_element(By.XPATH, error_indicator, timeout=2)
                if element:
                    self.logger.warning(f"Profile access issue detected: {error_indicator}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking profile accessibility: {str(e)}")
            return False
    
    def _collect_account_posts(self, account_username: str, post_count: int) -> List[Dict]:
        """
        Collect posts from a suspected account profile.
        
        Args:
            account_username: Username of the account
            post_count: Number of posts to collect
            
        Returns:
            List of post data dictionaries
        """
        posts = []
        collected_urls = set()
        
        try:
            self.logger.info(f"Collecting {post_count} posts from account: {account_username}")
            
            # Wait for posts to load
            time.sleep(5)
            
            # Scroll and collect posts
            for scroll_attempt in range(5):  # Maximum 5 scrolls
                # Find post elements - multiple selectors for different layouts
                post_selectors = [
                    "//article//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
                    "//div[@role='button']//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
                    "//a[contains(@href, '/" + account_username + "/p/') or contains(@href, '/" + account_username + "/reel/')]"
                ]
                
                post_elements = []
                for selector in post_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    post_elements.extend(elements)
                
                # Remove duplicates
                unique_elements = []
                seen_hrefs = set()
                for element in post_elements:
                    href = element.get_attribute('href')
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        unique_elements.append(element)
                
                self.logger.info(f"Found {len(unique_elements)} unique post elements on scroll {scroll_attempt + 1}")
                
                # Extract post data
                for element in unique_elements:
                    if len(posts) >= post_count:
                        break
                        
                    try:
                        post_url = element.get_attribute('href')
                        if post_url and post_url not in collected_urls:
                            collected_urls.add(post_url)
                            
                            # Extract additional data from the post element
                            post_data = {
                                'url': post_url,
                                'element': element,
                                'search_type': 'suspected_account',
                                'account_username': account_username,
                                'found_via': 'profile_page'
                            }
                            
                            # Try to extract preview data
                            try:
                                # Get post preview image if available
                                img_element = element.find_element(By.TAG_NAME, 'img')
                                if img_element:
                                    post_data['preview_image'] = img_element.get_attribute('src')
                            except NoSuchElementException:
                                pass
                            
                            posts.append(post_data)
                            self.logger.debug(f"Collected post: {post_url}")
                            
                    except Exception as e:
                        self.logger.warning(f"Error extracting post data: {str(e)}")
                        continue
                
                if len(posts) >= post_count:
                    break
                    
                # Scroll down to load more posts
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            
            self.logger.info(f"Successfully collected {len(posts)} posts from suspected account: {account_username}")
            return posts[:post_count]  # Return only requested number of posts
            
        except Exception as e:
            self.logger.error(f"Error collecting account posts: {str(e)}")
            return posts
    
    def get_account_info(self, account_username: str) -> Optional[Dict]:
        """
        Get basic information about the suspected account.
        
        Args:
            account_username: Username of the account
            
        Returns:
            Dictionary with account information or None if not accessible
        """
        try:
            self.logger.info(f"Retrieving account info for: {account_username}")
            
            # Navigate to profile if not already there
            current_url = self.driver.current_url
            expected_url = f"https://www.instagram.com/{account_username}/"
            
            if expected_url not in current_url:
                self.driver.get(expected_url)
                time.sleep(5)
            
            if not self._is_profile_accessible():
                return None
            
            account_info = {
                'username': account_username,
                'profile_url': expected_url,
                'is_accessible': True
            }
            
            # Try to extract additional profile information
            try:
                # Profile name/full name
                name_element = self._wait_for_element(
                    By.XPATH,
                    "//header//h2 | //header//span[contains(@class, 'name')]",
                    timeout=3
                )
                if name_element:
                    account_info['full_name'] = name_element.text.strip()
                
                # Post count
                posts_count_element = self._wait_for_element(
                    By.XPATH,
                    "//a[contains(@href, '/p/') or contains(text(), 'posts') or contains(text(), 'post')]//span[contains(text(), ',') or @title]",
                    timeout=3
                )
                if posts_count_element:
                    posts_text = posts_count_element.get_attribute('title') or posts_count_element.text
                    account_info['posts_count'] = posts_text.strip()
                
                # Bio/description
                bio_element = self._wait_for_element(
                    By.XPATH,
                    "//header//div[contains(@class, 'bio') or contains(@data-testid, 'bio')]",
                    timeout=3
                )
                if bio_element:
                    account_info['bio'] = bio_element.text.strip()
                    
            except Exception as e:
                self.logger.debug(f"Error extracting additional account info: {str(e)}")
            
            self.logger.info(f"Successfully retrieved account info for: {account_username}")
            return account_info
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def _wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present and return it."""
        if timeout is None:
            timeout = self.wait_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.logger.debug(f"Element not found: {by}={value}")
            return None
    
    def _wait_for_clickable(self, by, value, timeout=None):
        """Wait for an element to be clickable and return it."""
        if timeout is None:
            timeout = self.wait_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except TimeoutException:
            self.logger.debug(f"Element not clickable: {by}={value}")
            return None
    
    def verify_account_search_capability(self) -> bool:
        """
        Verify that account search functionality is working.
        
        Returns:
            True if account search is available, False otherwise
        """
        try:
            self.logger.info("Verifying account search capability")
            
            # Test with a known public account (Instagram's own account)
            test_account = "instagram"
            profile_url = f"https://www.instagram.com/{test_account}/"
            
            self.driver.get(profile_url)
            time.sleep(5)
            
            if self._is_profile_accessible():
                self.logger.info("Account search capability verified")
                return True
            else:
                self.logger.warning("Account search capability not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying account search capability: {str(e)}")
            return False
    
    def search_by_account(self, account_username: str, post_count: int = 10) -> List[Dict]:
        """
        Wrapper function for suspected account search for compatibility.
        
        Args:
            account_username: Username of suspected account to search
            post_count: Number of posts to retrieve
            
        Returns:
            List of post URLs found for the suspected account
        """
        return self.search_by_suspected_account(account_username, post_count)
