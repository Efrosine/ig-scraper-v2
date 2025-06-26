"""
Instagram Profile Scraper - Location Search Module
Phase 5: Search by Location

This module implements location-based search functionality with its specific algorithm.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LocationSearcher:
    """Handles location-based Instagram search functionality."""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.wait_timeout = 10
        
    def search_by_location(self, location: str, post_count: int = 10) -> List[Dict]:
        """
        Search Instagram posts by location using improved algorithm.
        
        Args:
            location: Location name to search for
            post_count: Number of posts to retrieve
            
        Returns:
            List of post URLs found for the location
        """
        try:
            self.logger.info(f"Starting improved location-based search for: {location}")
            
            # Try multiple approaches for location search
            approaches = [
                self._approach_1_explore_search,
                self._approach_2_direct_search,
                self._approach_3_hashtag_location
            ]
            
            for i, approach in enumerate(approaches, 1):
                self.logger.info(f"Trying location search approach {i}")
                try:
                    posts = approach(location, post_count)
                    if posts:
                        self.logger.info(f"Approach {i} successful: found {len(posts)} posts")
                        return posts
                except Exception as e:
                    self.logger.warning(f"Approach {i} failed: {str(e)}")
                    continue
            
            self.logger.warning(f"All location search approaches failed for: {location}")
            return []
                        
        except Exception as e:
            self.logger.error(f"Error in location search: {str(e)}")
            return []
    
    def _approach_1_explore_search(self, location: str, post_count: int) -> List[Dict]:
        """Approach 1: Use explore page search functionality."""
        self.logger.info("Approach 1: Using explore page search")
        
        # Navigate to Instagram explore page
        self.driver.get("https://www.instagram.com/explore/")
        time.sleep(5)
        
        # Try multiple search element selectors
        search_selectors = [
            "//input[@placeholder='Search']",
            "//input[@aria-label='Search input']",
            "//input[contains(@placeholder, 'Search')]",
            "//div[@role='button']//span[contains(text(), 'Search')]/..",
            "//a[contains(@href, '/explore/search/')]",
            "//svg[@aria-label='Search']/..",
            "//div[contains(@class, 'search')]//input"
        ]
        
        search_element = None
        for selector in search_selectors:
            search_element = self._wait_for_clickable(By.XPATH, selector, timeout=3)
            if search_element:
                self.logger.info(f"Found search element with selector: {selector}")
                break
        
        if not search_element:
            raise Exception("No search element found with any selector")
        
        # Click search element
        search_element.click()
        time.sleep(3)
        
        # Find search input field
        search_input = self._wait_for_element(By.XPATH, "//input", timeout=5)
        if not search_input:
            raise Exception("Search input field not found")
        
        # Enter location search
        search_input.clear()
        search_input.send_keys(location)
        time.sleep(3)
        
        # Look for and click places/locations tab
        places_selectors = [
            "//div[contains(text(), 'Places')]",
            "//div[contains(text(), 'Locations')]", 
            "//span[contains(text(), 'Places')]",
            "//span[contains(text(), 'Locations')]",
            "//a[contains(text(), 'Places')]"
        ]
        
        places_tab = None
        for selector in places_selectors:
            places_tab = self._wait_for_clickable(By.XPATH, selector, timeout=3)
            if places_tab:
                break
        
        if places_tab:
            places_tab.click()
            time.sleep(3)
            
            # Click on first location result
            location_result = self._wait_for_clickable(
                By.XPATH,
                f"//div[contains(text(), '{location}') or contains(@title, '{location}')]"
            )
            
            if location_result:
                location_result.click()
                time.sleep(5)
                return self._collect_location_posts(post_count)
        
        raise Exception("Could not navigate to location page")
    
    def _approach_2_direct_search(self, location: str, post_count: int) -> List[Dict]:
        """Approach 2: Try direct URL navigation for location."""
        self.logger.info("Approach 2: Using direct URL navigation")
        
        # Try common location URL patterns including the new hashtag keyword approach
        location_encoded = location.replace(" ", "%20").lower()
        url_patterns = [
            f"https://www.instagram.com/explore/search/keyword/?q=%23kota{location_encoded}",
            f"https://www.instagram.com/explore/search/keyword/?q=%23{location_encoded}",
            f"https://www.instagram.com/explore/search/keyword/?q=%23wisata{location_encoded}",
            f"https://www.instagram.com/explore/search/keyword/?q=%23{location_encoded}city",
            f"https://www.instagram.com/explore/locations/{location_encoded}/",
            f"https://www.instagram.com/explore/tags/{location_encoded}/",
            f"https://www.instagram.com/explore/search/keyword/?q={location_encoded}"
        ]
        
        for url in url_patterns:
            try:
                self.logger.info(f"Trying URL: {url}")
                self.driver.get(url)
                time.sleep(5)
                
                # Check if we landed on a valid page with posts
                post_elements = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@href, '/p/') or contains(@href, '/reel/')]"
                )
                
                if len(post_elements) > 0:
                    self.logger.info(f"Found posts via direct URL: {url}")
                    return self._collect_current_page_posts(post_count)
                    
            except Exception as e:
                self.logger.debug(f"URL {url} failed: {str(e)}")
                continue
        
        raise Exception("No direct URL approach worked")
    
    def _approach_3_hashtag_location(self, location: str, post_count: int) -> List[Dict]:
        """Approach 3: Search via hashtag related to location."""
        self.logger.info("Approach 3: Using hashtag-based location search")
        
        # Try location-related hashtags
        hashtags = [
            f"#{location.lower()}",
            f"#{location.lower().replace(' ', '')}",
            f"#wisata{location.lower()}",
            f"#kota{location.lower()}",
            f"#{location.lower()}city"
        ]
        
        for hashtag in hashtags:
            try:
                hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag.replace('#', '')}/"
                self.logger.info(f"Trying hashtag: {hashtag_url}")
                
                self.driver.get(hashtag_url)
                time.sleep(5)
                
                # Check if hashtag page loaded successfully
                post_elements = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@href, '/p/') or contains(@href, '/reel/')]"
                )
                
                if len(post_elements) > 0:
                    self.logger.info(f"Found posts via hashtag: {hashtag}")
                    return self._collect_current_page_posts(post_count)
                    
            except Exception as e:
                self.logger.debug(f"Hashtag {hashtag} failed: {str(e)}")
                continue
        
        raise Exception("No hashtag approach worked")
    
    def _collect_current_page_posts(self, post_count: int) -> List[Dict]:
        """Collect posts from current page (used by multiple approaches)."""
        posts = []
        collected_urls = set()
        
        try:
            self.logger.info(f"Collecting posts from current page, target: {post_count}")
            
            # Scroll and collect posts
            for scroll_attempt in range(3):  # Reduced scrolls for efficiency
                # Find post elements with multiple selectors
                post_selectors = [
                    "//article//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
                    "//div[@role='button']//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
                    "//a[contains(@href, '/p/') or contains(@href, '/reel/')]"
                ]
                
                post_elements = []
                for selector in post_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    post_elements.extend(elements)
                
                # Remove duplicates
                unique_elements = []
                seen_hrefs = set()
                for element in post_elements:
                    try:
                        href = element.get_attribute('href')
                        if href and href not in seen_hrefs:
                            seen_hrefs.add(href)
                            unique_elements.append(element)
                    except:
                        continue
                
                self.logger.info(f"Found {len(unique_elements)} unique post elements on scroll {scroll_attempt + 1}")
                
                # Extract post data
                for element in unique_elements:
                    if len(posts) >= post_count:
                        break
                        
                    try:
                        post_url = element.get_attribute('href')
                        if post_url and post_url not in collected_urls:
                            collected_urls.add(post_url)
                            
                            post_data = {
                                'url': post_url,
                                'element': element,
                                'search_type': 'location',
                                'found_via': 'improved_location_search'
                            }
                            
                            posts.append(post_data)
                            self.logger.debug(f"Collected post: {post_url}")
                            
                    except Exception as e:
                        self.logger.warning(f"Error extracting post data: {str(e)}")
                        continue
                
                if len(posts) >= post_count:
                    break
                    
                # Scroll down to load more posts
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            self.logger.info(f"Successfully collected {len(posts)} posts from current page")
            return posts[:post_count]
            
        except Exception as e:
            self.logger.error(f"Error collecting posts from current page: {str(e)}")
            return posts
    
    def _collect_location_posts(self, post_count: int) -> List[Dict]:
        """
        Collect posts from a location page.
        
        Args:
            post_count: Number of posts to collect
            
        Returns:
            List of post data dictionaries
        """
        posts = []
        collected_urls = set()
        
        try:
            self.logger.info(f"Collecting {post_count} posts from location page")
            
            # Wait for posts to load
            time.sleep(5)
            
            # Scroll and collect posts
            for scroll_attempt in range(5):  # Maximum 5 scrolls
                # Find post elements
                post_elements = self.driver.find_elements(
                    By.XPATH,
                    "//article//a[contains(@href, '/p/') or contains(@href, '/reel/')]"
                )
                
                self.logger.info(f"Found {len(post_elements)} post elements on scroll {scroll_attempt + 1}")
                
                # Extract post data
                for element in post_elements:
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
                                'search_type': 'location',
                                'found_via': 'location_page'
                            }
                            
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
            
            self.logger.info(f"Successfully collected {len(posts)} posts from location search")
            return posts[:post_count]  # Return only requested number of posts
            
        except Exception as e:
            self.logger.error(f"Error collecting location posts: {str(e)}")
            return posts
    
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
    
    def verify_location_search_capability(self) -> bool:
        """
        Verify that location search functionality is working.
        
        Returns:
            True if location search is available, False otherwise
        """
        try:
            self.logger.info("Verifying location search capability")
            
            # Navigate to explore page
            self.driver.get("https://www.instagram.com/explore/")
            time.sleep(3)
            
            # Check if search functionality is available
            search_element = self._wait_for_element(
                By.XPATH,
                "//input[@placeholder='Search' or @aria-label='Search input'] | //div[@role='button' and contains(@aria-label, 'Search')]"
            )
            
            if search_element:
                self.logger.info("Location search capability verified")
                return True
            else:
                self.logger.warning("Location search capability not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying location search capability: {str(e)}")
            return False
