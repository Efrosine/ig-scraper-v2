"""
Instagram Profile Scraper - HTML Parser Module
Phase 4: Advanced Parsing & Cleaning

This module handles HTML parsing and post data extraction using BeautifulSoup.
Enhanced with advanced parsing techniques and quality scoring.
"""

import re
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from bs4 import BeautifulSoup, Comment
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils import setup_logging
from data_cleaner import DataCleaner


class InstagramPostParser:
    """Enhanced parser for Instagram post data extraction with BeautifulSoup."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.data_cleaner = DataCleaner()
        
    def extract_post_data(self, driver, post_count: int = 10, comment_count: int = 5) -> List[Dict[str, Any]]:
        """
        Extract post data from Instagram profile page with enhanced parsing.
        
        Args:
            driver: Selenium WebDriver instance
            post_count: Number of posts to extract
            comment_count: Number of comments per post to extract
            
        Returns:
            List of cleaned post data dictionaries
        """
        posts_data = []
        
        try:
            self.logger.info(f"Starting enhanced post extraction: {post_count} posts, {comment_count} comments each")
            
            # Scroll to load posts
            self._scroll_to_load_posts(driver, post_count)
            
            # Get all post links
            post_links = self._get_post_links(driver, post_count)
            
            self.logger.info(f"Found {len(post_links)} post links")
            
            # Extract data from each post
            for i, post_url in enumerate(post_links[:post_count]):
                try:
                    self.logger.info(f"Processing post {i+1}/{post_count}: {post_url}")
                    
                    post_data = self._extract_single_post_data_enhanced(driver, post_url, comment_count)
                    if post_data:
                        # Clean and enhance the data
                        cleaned_data = self.data_cleaner.clean_post_data(post_data)
                        posts_data.append(cleaned_data)
                        
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing post {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in post extraction: {str(e)}")
            
        self.logger.info(f"Successfully extracted and cleaned {len(posts_data)} posts")
        return posts_data
    
    def _scroll_to_load_posts(self, driver, post_count: int):
        """Scroll the page to load more posts."""
        try:
            self.logger.info("Scrolling to load posts...")
            
            # Initial scroll to load first posts
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(3)
            
            # Continue scrolling until we have enough posts or reach the end
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while scroll_attempts < max_scroll_attempts:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Check if we have enough posts
                try:
                    posts = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/'], article a[href*='/reel/']")
                    if len(posts) >= post_count:
                        break
                except:
                    pass
                
                # Check if we've reached the bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
            self.logger.info(f"Scrolling completed after {scroll_attempts} attempts")
            
        except Exception as e:
            self.logger.error(f"Error during scrolling: {str(e)}")
    
    def _get_post_links(self, driver, post_count: int) -> List[str]:
        """Extract post URLs from the profile page."""
        post_links = []
        
        try:
            # Wait for posts to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            
            # Find all post links
            link_elements = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/'], article a[href*='/reel/']")
            
            for element in link_elements[:post_count]:
                href = element.get_attribute('href')
                if href and href not in post_links:
                    post_links.append(href)
                    
        except Exception as e:
            self.logger.error(f"Error getting post links: {str(e)}")
            
        return post_links
    
    def _extract_single_post_data_enhanced(self, driver, post_url: str, comment_count: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single post using enhanced BeautifulSoup parsing."""
        try:
            # Navigate to post
            driver.get(post_url)
            time.sleep(3)
            
            # Wait for post to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Get page source and create BeautifulSoup object
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract data using multiple methods
            post_data = {
                "usernamePost": self._extract_username_enhanced(driver, soup),
                "urlPost": post_url,
                "releaseDate": self._extract_release_date_enhanced(driver, soup),
                "caption": self._extract_caption_enhanced(driver, soup),
                "comments": self._extract_comments_enhanced(driver, soup, comment_count)
            }
            
            self.logger.info(f"Successfully extracted enhanced post data for {post_data['usernamePost']}")
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error extracting enhanced post data from {post_url}: {str(e)}")
            return None
    
    def _extract_username_enhanced(self, driver, soup: BeautifulSoup) -> str:
        """Extract username using enhanced BeautifulSoup parsing."""
        try:
            # Method 1: BeautifulSoup JSON-LD extraction
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict) and 'author' in json_data:
                        author = json_data['author']
                        if isinstance(author, dict) and 'alternateName' in author:
                            return author['alternateName'].lstrip('@')
                except:
                    continue
            
            # Method 2: Meta property extraction
            meta_elements = soup.find_all('meta', property=re.compile(r'.*:username'))
            for meta in meta_elements:
                content = meta.get('content', '')
                if content:
                    return content.lstrip('@')
            
            # Method 3: URL pattern extraction from soup
            links = soup.find_all('a', href=re.compile(r'instagram\.com/[^/]+/?$'))
            for link in links:
                href = link.get('href', '')
                match = re.search(r'instagram\.com/([^/]+)/?$', href)
                if match:
                    return match.group(1)
            
            # Method 4: Selenium fallback (existing method)
            return self._extract_username_selenium_fallback(driver)
            
        except Exception as e:
            self.logger.error(f"Error in enhanced username extraction: {str(e)}")
            return self._extract_username_selenium_fallback(driver)
    
    def _extract_release_date_enhanced(self, driver, soup: BeautifulSoup) -> str:
        """Extract release date using enhanced parsing."""
        try:
            # Method 1: BeautifulSoup time element
            time_elements = soup.find_all('time')
            for time_elem in time_elements:
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    try:
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        return dt.isoformat()
                    except:
                        continue
            
            # Method 2: JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        date_published = json_data.get('datePublished') or json_data.get('uploadDate')
                        if date_published:
                            dt = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
                            return dt.isoformat()
                except:
                    continue
            
            # Method 3: Meta tags
            meta_date = soup.find('meta', property=re.compile(r'.*:published_time|.*:upload_date'))
            if meta_date:
                content = meta_date.get('content', '')
                if content:
                    try:
                        dt = datetime.fromisoformat(content.replace('Z', '+00:00'))
                        return dt.isoformat()
                    except:
                        pass
            
            # Fallback to current time
            return datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            self.logger.error(f"Error in enhanced release date extraction: {str(e)}")
            return datetime.now(timezone.utc).isoformat()
    
    def _extract_caption_enhanced(self, driver, soup: BeautifulSoup) -> str:
        """Extract caption using enhanced BeautifulSoup parsing."""
        try:
            # Method 1: JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        caption = json_data.get('caption') or json_data.get('description') or json_data.get('text')
                        if caption and len(caption.strip()) > 5:
                            return caption.strip()
                except:
                    continue
            
            # Method 2: Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content', '')
                if content and len(content.strip()) > 10:
                    # Remove common Instagram meta prefixes
                    content = re.sub(r'^.*?on Instagram:\s*"?', '', content)
                    content = re.sub(r'"?\s*$', '', content)
                    if len(content.strip()) > 5:
                        return content.strip()
            
            # Method 3: Article content with specific selectors
            caption_selectors = [
                'article h1',
                'article [data-testid="post-caption"]',
                'article div[role="button"] span[dir="auto"]',
                'article span[dir="auto"]'
            ]
            
            for selector in caption_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        # Filter out obvious non-captions
                        if not self._is_likely_caption(text):
                            continue
                        return text
            
            # Method 4: Selenium fallback
            return self._extract_caption_selenium_fallback(driver)
            
        except Exception as e:
            self.logger.error(f"Error in enhanced caption extraction: {str(e)}")
            return ""
    
    def _extract_comments_enhanced(self, driver, soup: BeautifulSoup, comment_count: int) -> Dict[str, str]:
        """Extract comments using enhanced BeautifulSoup parsing."""
        comments = {}
        
        try:
            # First, try to load more comments using Selenium
            self._load_more_comments(driver)
            
            # Get fresh page source after loading comments
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Method 1: JSON data extraction
            json_scripts = soup.find_all('script', type='application/json')
            comment_texts = []
            
            for script in json_scripts:
                try:
                    json_str = script.string
                    if json_str and 'comment' in json_str.lower():
                        # Look for comment patterns in JSON
                        comment_patterns = [
                            r'"text":"([^"]+)"',
                            r'"comment":"([^"]+)"',
                            r'"body":"([^"]+)"'
                        ]
                        
                        for pattern in comment_patterns:
                            matches = re.findall(pattern, json_str)
                            for match in matches:
                                if len(match.strip()) > 3 and self._is_likely_comment(match):
                                    comment_texts.append(match.strip())
                except:
                    continue
            
            # Method 2: HTML structure parsing
            if len(comment_texts) < comment_count:
                comment_containers = soup.find_all(['div', 'li', 'span'], 
                    attrs={'role': ['button', 'listitem']})
                
                for container in comment_containers:
                    text_elements = container.find_all(['span', 'div'], 
                        attrs={'dir': 'auto'})
                    
                    for element in text_elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 3 and self._is_likely_comment(text):
                            if text not in comment_texts:
                                comment_texts.append(text)
            
            # Method 3: Selenium fallback for additional comments
            if len(comment_texts) < comment_count:
                selenium_comments = self._extract_comments_selenium_fallback(driver, comment_count)
                for comment in selenium_comments.values():
                    if comment not in comment_texts:
                        comment_texts.append(comment)
            
            # Format as numbered dictionary
            for i, comment_text in enumerate(comment_texts[:comment_count]):
                comments[str(i)] = comment_text
                
            self.logger.info(f"Extracted {len(comments)} enhanced comments")
            
        except Exception as e:
            self.logger.error(f"Error in enhanced comment extraction: {str(e)}")
            
        return comments
    
    def _load_more_comments(self, driver):
        """Load more comments using various strategies."""
        try:
            # Strategy 1: Click "View more comments" buttons
            view_more_selectors = [
                "button[aria-label*='comment']",
                "button[aria-label*='View']",
                "div[role='button'][tabindex='0']"
            ]
            
            for selector in view_more_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        aria_label = element.get_attribute('aria-label') or ''
                        if any(word in aria_label.lower() for word in ['comment', 'view', 'more']):
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(1)
                            break
                except:
                    continue
            
            # Strategy 2: Scroll within comment area
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
        except Exception as e:
            self.logger.debug(f"Error loading more comments: {str(e)}")
    
    def _is_likely_caption(self, text: str) -> bool:
        """Check if text is likely to be a caption."""
        # Filter out common non-caption text
        non_caption_indicators = [
            text.isdigit(),
            len(text) < 5,
            text.lower() in ['like', 'comment', 'share', 'follow', 'view', 'more', 'less'],
            re.match(r'^\d+[smhd]$', text),  # Time indicators
            text.startswith('View') and len(text.split()) <= 3,
            text == '•',
            re.match(r'^@\w+$', text)  # Just a single mention
        ]
        
        return not any(non_caption_indicators)
    
    def _is_likely_comment(self, text: str) -> bool:
        """Check if text is likely to be a comment (enhanced version)."""
        # More sophisticated comment filtering
        non_comment_indicators = [
            len(text) < 3,
            text.isdigit(),
            text.lower() in ['like', 'reply', 'view replies', 'hide replies', 'more', 'less'],
            text.startswith('@') and len(text.split()) == 1,  # Just a mention
            re.match(r'^\d+[smhd]$', text),  # Time indicators like "5m", "1h"
            text in ['•', '...', '❤️', '👍', '🔥'],  # Common reaction symbols
            re.match(r'^\d+\s*(like|comment|share|view)s?$', text.lower()),
            len(text) > 500,  # Probably not a comment if too long
            text.count('\n') > 5  # Too many line breaks
        ]
        
        return not any(non_comment_indicators)
    
    # Fallback methods using original Selenium approach
    def _extract_username_selenium_fallback(self, driver) -> str:
        """Fallback username extraction using Selenium."""
        try:
            # Try multiple selectors for username
            selectors = [
                "article header a[role='link']",
                "article header h2 a",
                "a[href*='/'][dir='ltr']",
                "header a[href^='/']"
            ]
            
            for selector in selectors:
                try:
                    username_element = driver.find_element(By.CSS_SELECTOR, selector)
                    username = username_element.get_attribute('href').split('/')[-2]
                    if username and username != '':
                        return username
                except:
                    continue
                    
            # Fallback: try to get from URL
            current_url = driver.current_url
            if '/p/' in current_url or '/reel/' in current_url:
                # Try to get username from page source
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Look for username in various places
                username_patterns = [
                    r'"username":"([^"]+)"',
                    r'"owner":{"username":"([^"]+)"',
                    r'instagram.com/([^/]+)/'
                ]
                
                for pattern in username_patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        return matches[0]
                        
            return "unknown_user"
            
        except Exception as e:
            self.logger.error(f"Error extracting username: {str(e)}")
            return "unknown_user"
    
    def _extract_release_date(self, driver) -> str:
        """Extract post release date."""
        try:
            # Try to find time element
            time_elements = driver.find_elements(By.CSS_SELECTOR, "time")
            
            if time_elements:
                for time_elem in time_elements:
                    datetime_attr = time_elem.get_attribute('datetime')
                    if datetime_attr:
                        # Parse and format the datetime
                        try:
                            dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                            return dt.isoformat()
                        except:
                            return datetime_attr
                            
            # Fallback: use current time if we can't find the actual time
            return datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            self.logger.error(f"Error extracting release date: {str(e)}")
            return datetime.now(timezone.utc).isoformat()
    
    def _extract_caption(self, driver) -> str:
        """Extract post caption."""
        try:
            # Try multiple selectors for caption
            caption_selectors = [
                "article div[data-testid='post-caption'] span",
                "article h1",
                "div[role='button'] span",
                "article span[dir='auto']"
            ]
            
            for selector in caption_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('textContent') or element.text
                        if text and len(text.strip()) > 10:  # Ensure it's substantial text
                            return text.strip()
                except:
                    continue
                    
            # Fallback: try to extract from page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for caption in JSON-LD or other structured data
            caption_patterns = [
                r'"caption":"([^"]+)"',
                r'"text":"([^"]+)"',
                r'"description":"([^"]+"'
            ]
            
            for pattern in caption_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    # Get the longest match as it's likely the caption
                    longest_match = max(matches, key=len)
                    if len(longest_match) > 10:
                        return longest_match
                        
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting caption: {str(e)}")
            return ""
    
    def _extract_comments(self, driver, comment_count: int) -> Dict[str, str]:
        """Extract comments from post."""
        comments = {}
        
        try:
            # Try to scroll to load comments
            try:
                # Look for "View comments" button or similar
                view_comments_selectors = [
                    "button[aria-label*='comment']",
                    "a[href*='comments']",
                    "div[role='button'][tabindex='0']"
                ]
                
                for selector in view_comments_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if 'comment' in element.get_attribute('aria-label', '').lower():
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)
                                break
                    except:
                        continue
            except:
                pass
            
            # Scroll to load more comments
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Extract comments using multiple strategies
            comment_elements = []
            
            # Strategy 1: Look for comment containers
            comment_selectors = [
                "div[role='button'] span[dir='auto']",
                "article span[dir='auto']",
                "div[data-testid*='comment'] span",
                "ul li span[dir='auto']"
            ]
            
            for selector in comment_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    comment_elements.extend(elements)
                except:
                    continue
            
            # Filter and extract comment text
            comment_texts = []
            for element in comment_elements:
                try:
                    text = element.get_attribute('textContent') or element.text
                    if text and len(text.strip()) > 3:
                        # Filter out obvious non-comments (like usernames, timestamps, etc.)
                        text = text.strip()
                        if not self._is_likely_comment(text):
                            continue
                        if text not in comment_texts:
                            comment_texts.append(text)
                except:
                    continue
            
            # Format comments as numbered dictionary
            for i, comment_text in enumerate(comment_texts[:comment_count]):
                comments[str(i)] = comment_text
                
            self.logger.info(f"Extracted {len(comments)} comments")
            
        except Exception as e:
            self.logger.error(f"Error extracting comments: {str(e)}")
            
        return comments
    
    def _is_likely_comment(self, text: str) -> bool:
        """Check if text is likely to be a comment."""
        # Filter out common non-comment text
        filters = [
            len(text) < 3,
            text.isdigit(),
            text in ['Like', 'Reply', 'View replies', 'Hide replies'],
            text.startswith('@') and len(text.split()) == 1,  # Just a mention
            re.match(r'^\d+[smhd]$', text),  # Time indicators like "5m", "1h"
            text in ['•', '...', 'more', 'less']
        ]
        
        return not any(filters)
    
    def extract_profile_posts(self, driver, username: str, post_count: int = 10, comment_count: int = 5) -> Dict[str, Any]:
        """
        Main method to extract posts from a profile.
        
        Args:
            driver: Selenium WebDriver instance
            username: Instagram username to scrape
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            
        Returns:
            Dictionary containing extracted posts data
        """
        try:
            self.logger.info(f"Starting profile post extraction for @{username}")
            
            # Navigate to profile
            profile_url = f"https://www.instagram.com/{username}/"
            driver.get(profile_url)
            time.sleep(5)
            
            # Wait for profile to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            
            # Extract posts
            posts_data = self.extract_post_data(driver, post_count, comment_count)
            
            # Format result
            result = {
                "username": username,
                "extraction_time": datetime.now(timezone.utc).isoformat(),
                "total_posts_extracted": len(posts_data),
                "requested_posts": post_count,
                "requested_comments_per_post": comment_count,
                "results": posts_data
            }
            
            self.logger.info(f"Profile post extraction completed for @{username}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in profile post extraction: {str(e)}")
            return {
                "username": username,
                "extraction_time": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "results": []
            }
    
    def _extract_caption_selenium_fallback(self, driver) -> str:
        """Fallback caption extraction using Selenium."""
        try:
            # Try multiple selectors for caption
            caption_selectors = [
                "article div[data-testid='post-caption'] span",
                "article h1",
                "div[role='button'] span",
                "article span[dir='auto']"
            ]
            
            for selector in caption_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('textContent') or element.text
                        if text and len(text.strip()) > 10:  # Ensure it's substantial text
                            return text.strip()
                except:
                    continue
                    
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting caption: {str(e)}")
            return ""
    
    def _extract_comments_selenium_fallback(self, driver, comment_count: int) -> Dict[str, str]:
        """Fallback comment extraction using Selenium."""
        comments = {}
        
        try:
            # Extract comments using multiple strategies
            comment_elements = []
            
            # Strategy 1: Look for comment containers
            comment_selectors = [
                "div[role='button'] span[dir='auto']",
                "article span[dir='auto']",
                "div[data-testid*='comment'] span",
                "ul li span[dir='auto']"
            ]
            
            for selector in comment_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    comment_elements.extend(elements)
                except:
                    continue
            
            # Filter and extract comment text
            comment_texts = []
            for element in comment_elements:
                try:
                    text = element.get_attribute('textContent') or element.text
                    if text and len(text.strip()) > 3:
                        # Filter out obvious non-comments (like usernames, timestamps, etc.)
                        text = text.strip()
                        if not self._is_likely_comment(text):
                            continue
                        if text not in comment_texts:
                            comment_texts.append(text)
                except:
                    continue
            
            # Format comments as numbered dictionary
            for i, comment_text in enumerate(comment_texts[:comment_count]):
                comments[str(i)] = comment_text
                
        except Exception as e:
            self.logger.error(f"Error extracting comments: {str(e)}")
            
        return comments
    
    def _scroll_to_load_posts(self, driver, post_count: int):
        """Scroll the page to load more posts."""
        try:
            self.logger.info("Scrolling to load posts...")
            
            # Initial scroll to load first posts
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(3)
            
            # Continue scrolling until we have enough posts or reach the end
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while scroll_attempts < max_scroll_attempts:
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Check if we have enough posts
                try:
                    posts = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/'], article a[href*='/reel/']")
                    if len(posts) >= post_count:
                        break
                except:
                    pass
                
                # Check if we've reached the bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
            self.logger.info(f"Scrolling completed after {scroll_attempts} attempts")
            
        except Exception as e:
            self.logger.error(f"Error during scrolling: {str(e)}")
    
    def _get_post_links(self, driver, post_count: int) -> List[str]:
        """Extract post URLs from the profile page."""
        post_links = []
        
        try:
            # Wait for posts to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            
            # Find all post links
            link_elements = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/'], article a[href*='/reel/']")
            
            for element in link_elements[:post_count]:
                href = element.get_attribute('href')
                if href and href not in post_links:
                    post_links.append(href)
                    
        except Exception as e:
            self.logger.error(f"Error getting post links: {str(e)}")
            
        return post_links
    
    def _extract_single_post_data(self, driver, post_url: str, comment_count: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single post (legacy method for compatibility)."""
        try:
            # Navigate to post
            driver.get(post_url)
            time.sleep(3)
            
            # Wait for post to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Extract username
            username = self._extract_username_selenium_fallback(driver)
            
            # Extract release date
            release_date = self._extract_release_date(driver)
            
            # Extract caption
            caption = self._extract_caption_selenium_fallback(driver)
            
            # Extract comments
            comments = self._extract_comments_selenium_fallback(driver, comment_count)
            
            post_data = {
                "usernamePost": username,
                "urlPost": post_url,
                "releaseDate": release_date,
                "caption": caption,
                "comments": comments
            }
            
            self.logger.info(f"Successfully extracted post data for {username}")
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error extracting post data from {post_url}: {str(e)}")
            return None
