"""
Instagram Profile Scraper - Core Scraper Module
Phase 1: Foundation, Login & Backup Accounts

This module provides the core scraping functionality with Selenium WebDriver.
"""

import time
import logging
import os
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)

from utils import SessionManager, RateLimiter, detect_chromedriver_path, setup_logging


class InstagramScraper:
    """Core Instagram scraper with login and session management."""
    
    def __init__(self):
        self.driver = None
        self.session_manager = SessionManager()
        self.rate_limiter = RateLimiter()
        self.logger = setup_logging()
        self.wait_timeout = 10
        
    def _setup_driver(self):
        """Set up Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1280,720")
            
            # DO NOT RUN HEADLESS - Keep GUI visible for Phase 2
            # chrome_options.add_argument("--headless")  # Commented out to show GUI
            
            # Disable images to speed up loading
            # prefs = {"profile.managed_default_content_settings.images": 2}
            # chrome_options.add_experimental_option("prefs", prefs)
            
            # User agent to avoid detection
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Get ChromeDriver path
            chromedriver_path = detect_chromedriver_path()
            self.logger.info(f"Using ChromeDriver at: {chromedriver_path}")
            
            # Create service and driver
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def _wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present and return it."""
        if timeout is None:
            timeout = self.wait_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {by}={value}")
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
            self.logger.error(f"Element not clickable: {by}={value}")
            return None
    
    def _handle_login_popups(self):
        """Handle common Instagram login popups and notifications."""
        try:
            # Handle "Save Login Info" popup
            save_info_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Save Info')]",
                "//button[@type='button' and contains(text(), 'Not now')]",
                "//div[@role='button' and contains(text(), 'Not Now')]"
            ]
            
            for selector in save_info_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        self.logger.info("Handled save login info popup")
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Handle notification popup
            notification_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Block')]",
                "//button[@type='button' and contains(text(), 'Not now')]"
            ]
            
            for selector in notification_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        self.logger.info("Handled notification popup")
                        time.sleep(2)
                        break
                except:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error handling popups: {str(e)}")
    
    def _check_login_success(self) -> bool:
        """Check if login was successful."""
        try:
            # Wait a bit for page to load
            time.sleep(3)
            
            # Check for common indicators of successful login
            success_indicators = [
                "//a[@href='/']",  # Home link
                "//span[contains(text(), 'Search')]",  # Search text
                "//svg[@aria-label='Home']",  # Home icon
                "//a[contains(@href, '/accounts/activity')]"  # Activity link
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element:
                        self.logger.info("Login success confirmed")
                        return True
                except:
                    continue
            
            # Check for error messages
            error_selectors = [
                "//div[contains(text(), 'incorrect')]",
                "//div[contains(text(), 'Sorry')]",
                "//div[contains(text(), 'error')]",
                "//p[contains(text(), 'incorrect')]"
            ]
            
            for selector in error_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        self.logger.error(f"Login error detected: {element.text}")
                        return False
                except:
                    continue
            
            # If we can't find clear indicators, check URL
            current_url = self.driver.current_url
            if "instagram.com/accounts/login" in current_url:
                self.logger.warning("Still on login page, login may have failed")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking login success: {str(e)}")
            return False
    
    def login_with_account(self, account: dict) -> bool:
        """Attempt to login with a specific account."""
        username = account['username']
        password = account['password']
        
        try:
            self.logger.info(f"Attempting login with account: {username}")
            
            # Apply rate limiting
            self.rate_limiter.wait_for_login()
            
            # Try to load existing session first
            if self.session_manager.load_session(self.driver, username):
                if self._check_login_success():
                    self.logger.info(f"Successfully loaded existing session for: {username}")
                    return True
                else:
                    self.logger.info("Existing session invalid, proceeding with fresh login")
                    self.session_manager.clear_session(username)
            
            # Navigate to login page
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            
            # Wait for and fill username
            username_input = self._wait_for_element(By.NAME, "username")
            if not username_input:
                self.logger.error("Username input field not found")
                return False
            
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)
            
            # Wait for and fill password
            password_input = self._wait_for_element(By.NAME, "password")
            if not password_input:
                self.logger.error("Password input field not found")
                return False
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            # Find and click submit button
            submit_button = self._wait_for_clickable(By.XPATH, "//button[@type='submit']")
            if not submit_button:
                # Try alternative selectors
                submit_selectors = [
                    "//div[@role='button' and contains(text(), 'Log In')]",
                    "//button[contains(text(), 'Log In')]",
                    "//input[@type='submit']"
                ]
                
                for selector in submit_selectors:
                    submit_button = self._wait_for_clickable(By.XPATH, selector)
                    if submit_button:
                        break
            
            if not submit_button:
                self.logger.error("Submit button not found")
                return False
            
            submit_button.click()
            self.logger.info("Login form submitted")
            
            # Wait for login to process
            time.sleep(5)
            
            # Handle popups
            self._handle_login_popups()
            
            # Check if login was successful
            if self._check_login_success():
                # Save session for future use
                self.session_manager.save_session(self.driver, username)
                self.logger.info(f"Successfully logged in with account: {username}")
                return True
            else:
                self.logger.error(f"Login failed for account: {username}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception during login with {username}: {str(e)}")
            return False
    
    def login_with_backup_support(self) -> bool:
        """Login with primary account and backup support."""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Try current account
            current_account = self.session_manager.get_current_account()
            
            if self.login_with_account(current_account):
                return True
            
            # Try backup accounts
            while True:
                backup_account = self.session_manager.switch_to_backup_account()
                if not backup_account:
                    self.logger.error("All accounts failed to login")
                    return False
                
                if self.login_with_account(backup_account):
                    return True
            
        except Exception as e:
            self.logger.error(f"Critical error during login process: {str(e)}")
            return False
    
    def take_screenshot(self, filename: str = None):
        """Take a screenshot for debugging purposes."""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            filepath = os.path.join("output", filename)
            os.makedirs("output", exist_ok=True)
            
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
    
    def close(self):
        """Close the WebDriver and clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def navigate_to_profile(self, username: str) -> bool:
        """
        Navigate to a specific Instagram profile.
        
        Args:
            username (str): Instagram username to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.logger.info(f"Navigating to profile: @{username}")
            
            # Construct profile URL
            profile_url = f"https://www.instagram.com/{username}/"
            
            # Navigate to profile
            self.driver.get(profile_url)
            self.rate_limiter.wait_for_request()
            
            # Wait for profile page to load
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Check if profile exists by looking for profile header
            try:
                # Look for profile header elements
                profile_header = wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "header section")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='user-avatar']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h2"))
                    )
                )
                
                # Check if we're on a valid profile page
                current_url = self.driver.current_url
                if f"/{username}/" in current_url.lower():
                    self.logger.info(f"Successfully navigated to profile: @{username}")
                    return True
                else:
                    self.logger.warning(f"Navigation to @{username} may have failed - URL: {current_url}")
                    return False
                    
            except TimeoutException:
                # Check if profile doesn't exist
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, "h2")
                    if "Sorry, this page isn't available" in error_message.text:
                        self.logger.error(f"Profile @{username} does not exist or is private")
                        return False
                except NoSuchElementException:
                    pass
                
                self.logger.error(f"Timeout waiting for profile @{username} to load")
                return False
                
        except Exception as e:
            self.logger.error(f"Error navigating to profile @{username}: {str(e)}")
            return False
    
    def extract_profile_data(self, username: str) -> Dict:
        """
        Extract basic profile data from current profile page.
        
        Args:
            username (str): Username of the profile
            
        Returns:
            Dict: Profile data dictionary
        """
        try:
            self.logger.info(f"Extracting profile data for @{username}")
            
            profile_data = {
                "username": username,
                "display_name": "",
                "bio": "",
                "followers_count": 0,
                "following_count": 0,
                "posts_count": 0,
                "is_private": False,
                "is_verified": False,
                "profile_pic_url": "",
                "external_url": "",
                "extraction_timestamp": time.time()
            }
            
            # Extract display name
            try:
                display_name_element = self.driver.find_element(By.CSS_SELECTOR, "h2")
                profile_data["display_name"] = display_name_element.text.strip()
                self.logger.info(f"Display name: {profile_data['display_name']}")
            except NoSuchElementException:
                self.logger.warning("Could not find display name")
            
            # Extract bio
            try:
                bio_element = self.driver.find_element(By.CSS_SELECTOR, "div._ac69 span")
                profile_data["bio"] = bio_element.text.strip()
                self.logger.info(f"Bio extracted: {len(profile_data['bio'])} characters")
            except NoSuchElementException:
                self.logger.warning("Could not find bio")
            
            # Extract follower/following/posts counts
            try:
                stats_elements = self.driver.find_elements(By.CSS_SELECTOR, "ul li span")
                for element in stats_elements:
                    text = element.text.strip()
                    if 'post' in text.lower():
                        profile_data["posts_count"] = self._extract_number_from_text(text)
                    elif 'follower' in text.lower():
                        profile_data["followers_count"] = self._extract_number_from_text(text)
                    elif 'following' in text.lower():
                        profile_data["following_count"] = self._extract_number_from_text(text)
                        
                self.logger.info(f"Stats - Posts: {profile_data['posts_count']}, "
                               f"Followers: {profile_data['followers_count']}, "
                               f"Following: {profile_data['following_count']}")
            except Exception as e:
                self.logger.warning(f"Could not extract stats: {str(e)}")
            
            # Check if profile is private
            try:
                private_indicator = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='private-account-icon']")
                profile_data["is_private"] = True
                self.logger.info("Profile is private")
            except NoSuchElementException:
                profile_data["is_private"] = False
                self.logger.info("Profile is public")
            
            # Check if profile is verified
            try:
                verified_indicator = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='verified-icon']")
                profile_data["is_verified"] = True
                self.logger.info("Profile is verified")
            except NoSuchElementException:
                profile_data["is_verified"] = False
            
            # Extract profile picture URL
            try:
                profile_pic = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='user-avatar'] img")
                profile_data["profile_pic_url"] = profile_pic.get_attribute('src')
                self.logger.info("Profile picture URL extracted")
            except NoSuchElementException:
                self.logger.warning("Could not find profile picture")
            
            # Extract external URL
            try:
                external_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='http']")
                profile_data["external_url"] = external_link.get_attribute('href')
                self.logger.info(f"External URL: {profile_data['external_url']}")
            except NoSuchElementException:
                self.logger.info("No external URL found")
            
            self.logger.info(f"Profile data extraction completed for @{username}")
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error extracting profile data for @{username}: {str(e)}")
            return profile_data
    
    def _extract_number_from_text(self, text: str) -> int:
        """
        Extract number from text like '1,234 posts', '5.6M followers', etc.
        
        Args:
            text (str): Text containing number
            
        Returns:
            int: Extracted number
        """
        try:
            # Remove common words and clean text
            text = text.lower().replace('posts', '').replace('followers', '').replace('following', '').strip()
            
            # Handle different number formats
            if 'k' in text:
                # Convert 1.2k to 1200
                number = float(text.replace('k', '').replace(',', ''))
                return int(number * 1000)
            elif 'm' in text:
                # Convert 1.2m to 1200000
                number = float(text.replace('m', '').replace(',', ''))
                return int(number * 1000000)
            else:
                # Handle regular numbers with commas
                number = text.replace(',', '').replace('.', '')
                return int(''.join(filter(str.isdigit, number)))
                
        except (ValueError, TypeError):
            return 0
    
    def scrape_posts(self, username: str, post_count: int = 10, comment_count: int = 5) -> Dict:
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
            self.logger.info(f"Starting post scraping for @{username}")
            
            # Navigate to profile first
            if not self.navigate_to_profile(username):
                return {"error": f"Failed to navigate to profile @{username}", "results": []}
            
            # Scroll to load posts
            self.logger.info("Scrolling to load posts...")
            self._scroll_to_load_posts(post_count)
            
            # Get post links
            post_links = self._get_post_links(post_count)
            if not post_links:
                return {"error": "No posts found", "results": []}
            
            self.logger.info(f"Found {len(post_links)} post links")
            
            # Scrape each post
            scraped_posts = []
            for i, post_url in enumerate(post_links[:post_count]):
                self.logger.info(f"Scraping post {i+1}/{min(post_count, len(post_links))}: {post_url}")
                
                try:
                    post_data = self._scrape_individual_post(post_url, comment_count)
                    if post_data:
                        scraped_posts.append(post_data)
                        
                    # Rate limiting between posts
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping post {post_url}: {str(e)}")
                    continue
            
            return {
                "results": scraped_posts,
                "total_scraped": len(scraped_posts),
                "requested_count": post_count,
                "username": username
            }
            
        except Exception as e:
            self.logger.error(f"Error in post scraping: {str(e)}")
            return {"error": str(e), "results": []}
    
    def _get_post_links(self, max_posts: int) -> List[str]:
        """Extract post links from the profile page using multiple strategies."""
        try:
            # Wait for posts to load
            time.sleep(3)
            
            post_links = []
            
            # Strategy 1: Use specific Instagram classes with role="link"
            post_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "a.x1i10hfl.xjbqb8w.x1ejq31n[role='link']"
            )
            self.logger.info(f"Strategy 1 found {len(post_elements)} elements")
            
            # Strategy 2: Use broader class selector if first strategy fails
            if not post_elements:
                self.logger.info("Strategy 1 failed, trying Strategy 2")
                post_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a.x1i10hfl.xjbqb8w.x1ejq31n"
                )
                self.logger.info(f"Strategy 2 found {len(post_elements)} elements")
            
            # Strategy 3: Fallback to original selector
            if not post_elements:
                self.logger.info("Strategy 2 failed, trying fallback selector")
                post_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "article a[href*='/p/'], article a[href*='/reel/']"
                )
                self.logger.info(f"Strategy 3 found {len(post_elements)} elements")
            
            # Extract and validate hrefs
            for element in post_elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        # Convert relative URLs to absolute URLs
                        if href.startswith('/'):
                            href = f"https://www.instagram.com{href}"
                        
                        # Validate that it's a post or reel URL
                        if (('/p/' in href) or ('/reel/' in href)) and 'instagram.com' in href:
                            post_links.append(href)
                            
                            # Stop when we have enough links
                            if len(post_links) >= max_posts:
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Error processing element: {str(e)}")
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_post_links = []
            for link in post_links:
                if link not in seen:
                    seen.add(link)
                    unique_post_links.append(link)
            
            self.logger.info(f"Extracted {len(unique_post_links)} unique post links")
            return unique_post_links[:max_posts]
            
        except Exception as e:
            self.logger.error(f"Error getting post links: {str(e)}")
            return []
    
    def _scrape_individual_post(self, post_url: str, comment_count: int) -> Dict:
        """
        Scrape data from an individual post.
        
        Returns:
            Dict with post data in the required format
        """
        try:
            # Navigate to post
            self.driver.get(post_url)
            time.sleep(3)
            
            # Take screenshot for debugging
            self.take_screenshot(f"post_scraping_{int(time.time())}.png")
            
            # Initialize post data
            post_data = {
                "usernamePost": "",
                "urlPost": post_url,
                "releaseDate": "",
                "caption": "",
                "comments": {}
            }
            
            # Extract username
            try:
                username_element = self.driver.find_element(By.CSS_SELECTOR, "article header a")
                post_data["usernamePost"] = username_element.text.strip()
            except:
                self.logger.warning("Could not extract username from post")
            
            # Extract release date
            try:
                # Look for time element
                time_elements = self.driver.find_elements(By.CSS_SELECTOR, "time")
                if time_elements:
                    datetime_attr = time_elements[0].get_attribute('datetime')
                    if datetime_attr:
                        post_data["releaseDate"] = datetime_attr
                    else:
                        post_data["releaseDate"] = time_elements[0].get_attribute('title') or ""
            except:
                self.logger.warning("Could not extract release date from post")
            
            # Extract caption
            try:
                # Multiple selectors for caption
                caption_selectors = [
                    "article div[data-testid='post-caption'] span",
                    "article div span:first-child",
                    "article div span[dir='auto']"
                ]
                
                for selector in caption_selectors:
                    try:
                        caption_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        caption_text = caption_element.text.strip()
                        if caption_text and len(caption_text) > 10:  # Reasonable caption length
                            post_data["caption"] = caption_text
                            break
                    except:
                        continue
                        
            except:
                self.logger.warning("Could not extract caption from post")
            
            # Extract comments
            try:
                post_data["comments"] = self._extract_comments(comment_count)
            except:
                self.logger.warning("Could not extract comments from post")
            
            self.logger.info(f"Successfully scraped post: {post_data['usernamePost']}")
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error scraping individual post {post_url}: {str(e)}")
            return None
    
    def _extract_comments(self, max_comments: int) -> Dict[str, str]:
        """Extract comments from the current post."""
        try:
            comments = {}
            
            # Try to load more comments if available
            try:
                load_more_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "button[aria-label*='more comments'], button[aria-label*='Load more comments']"
                )
                for button in load_more_buttons[:2]:  # Click up to 2 load more buttons
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                    except:
                        pass
            except:
                pass
            
            # Find comment elements
            comment_selectors = [
                "article div[role='button'] span[dir='auto']",
                "article div span[dir='auto']",
                "article ul li div span"
            ]
            
            comment_elements = []
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        comment_elements = elements
                        break
                except:
                    continue
            
            # Extract comment text
            comment_count = 0
            for element in comment_elements:
                if comment_count >= max_comments:
                    break
                    
                try:
                    comment_text = element.text.strip()
                    
                    # Filter out non-comment text (usernames, etc.)
                    if (comment_text and 
                        len(comment_text) > 3 and 
                        not comment_text.startswith('@') and
                        '•' not in comment_text and
                        'ago' not in comment_text.lower() and
                        'like' not in comment_text.lower() and
                        'reply' not in comment_text.lower()):
                        
                        comments[str(comment_count)] = comment_text
                        comment_count += 1
                        
                except:
                    continue
            
            self.logger.info(f"Extracted {len(comments)} comments")
            return comments
            
        except Exception as e:
            self.logger.error(f"Error extracting comments: {str(e)}")
            return {}

    def _scroll_to_load_posts(self, target_count: int):
        """Scroll to load enough posts for scraping using multi-strategy approach."""
        try:
            self.logger.info(f"Scrolling to load at least {target_count} posts")
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 10
            
            while scroll_attempts < max_scrolls:
                # Check current post count using multiple strategies
                posts = []
                
                # Strategy 1: Specific Instagram classes with role
                posts = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a.x1i10hfl.xjbqb8w.x1ejq31n[role='link']"
                )
                
                # Strategy 2: Broader class selector
                if not posts:
                    posts = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "a.x1i10hfl.xjbqb8w.x1ejq31n"
                    )
                
                # Strategy 3: Fallback to original selector
                if not posts:
                    posts = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "article a[href*='/p/'], article a[href*='/reel/']"
                    )
                
                # Filter valid post links
                valid_posts = []
                for post in posts:
                    try:
                        href = post.get_attribute('href')
                        if href and (('/p/' in href) or ('/reel/' in href)):
                            valid_posts.append(post)
                    except:
                        continue
                
                current_post_count = len(valid_posts)
                
                if current_post_count >= target_count:
                    self.logger.info(f"Found {current_post_count} valid posts, sufficient for target {target_count}")
                    break
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Reduced wait time for faster scrolling
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    self.logger.info("Reached bottom of page")
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
                self.logger.info(f"Scroll attempt {scroll_attempts}, found {current_post_count} valid posts")
            
        except Exception as e:
            self.logger.error(f"Error during post loading scroll: {str(e)}")

    def close(self):
        """Close the WebDriver instance."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {str(e)}")
