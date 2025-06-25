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
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # DO NOT RUN HEADLESS - Keep GUI visible for Phase 2
            # chrome_options.add_argument("--headless")  # Commented out to show GUI
            
            # Disable images to speed up loading
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            
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
