"""
Instagram Profile Scraper - Data Cleaner Module
Phase 4: Advanced Parsing & Cleaning

This module handles data cleaning, text normalization, and entity decoding.
"""

import re
import html
import unicodedata
import emoji
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from urllib.parse import unquote

from utils import setup_logging


class DataCleaner:
    """Data cleaning and normalization for Instagram post data."""
    
    def __init__(self):
        self.logger = setup_logging()
        
    def clean_post_data(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize post data.
        
        Args:
            post_data: Raw post data dictionary
            
        Returns:
            Cleaned post data dictionary
        """
        try:
            cleaned_data = {
                "usernamePost": self.clean_username(post_data.get("usernamePost", "")),
                "urlPost": self.clean_url(post_data.get("urlPost", "")),
                "releaseDate": self.clean_release_date(post_data.get("releaseDate", "")),
                "caption": self.clean_caption(post_data.get("caption", "")),
                "comments": self.clean_comments(post_data.get("comments", {}))
            }
            
            # Add quality scoring
            cleaned_data["quality_score"] = self.calculate_quality_score(cleaned_data)
            
            # Extract metadata
            cleaned_data["metadata"] = self.extract_metadata(cleaned_data)
            
            self.logger.debug(f"Cleaned post data for user: {cleaned_data['usernamePost']}")
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error cleaning post data: {str(e)}")
            return post_data
    
    def clean_username(self, username: str) -> str:
        """Clean and validate username."""
        if not username:
            return "unknown_user"
            
        # Remove any leading/trailing whitespace
        username = username.strip()
        
        # Extract username from URL if needed
        if username.startswith('http'):
            username = self._extract_username_from_url(username)
        
        # Remove @ symbol if present
        username = username.lstrip('@')
        
        # Validate username format (Instagram usernames: alphanumeric, dots, underscores)
        username = re.sub(r'[^a-zA-Z0-9._]', '', username)
        
        return username if username else "unknown_user"
    
    def clean_url(self, url: str) -> str:
        """Clean and normalize post URL."""
        if not url:
            return ""
            
        # Remove any whitespace
        url = url.strip()
        
        # Decode URL if needed
        url = unquote(url)
        
        # Ensure it's a valid Instagram URL
        if not url.startswith('https://www.instagram.com/'):
            if url.startswith('/p/') or url.startswith('/reel/'):
                url = f"https://www.instagram.com{url}"
        
        return url
    
    def clean_release_date(self, release_date: str) -> str:
        """Clean and normalize release date."""
        if not release_date:
            return datetime.now(timezone.utc).isoformat()
        
        try:
            # Handle various datetime formats
            release_date = release_date.strip()
            
            # If it's already in ISO format, validate it
            if 'T' in release_date:
                dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                return dt.isoformat()
            
            # Handle timestamp format
            if release_date.isdigit():
                dt = datetime.fromtimestamp(int(release_date), tz=timezone.utc)
                return dt.isoformat()
                
        except Exception as e:
            self.logger.warning(f"Could not parse release date '{release_date}': {str(e)}")
        
        # Fallback to current time
        return datetime.now(timezone.utc).isoformat()
    
    def clean_caption(self, caption: str) -> str:
        """Clean and normalize caption text."""
        if not caption:
            return ""
        
        # HTML decode
        caption = html.unescape(caption)
        
        # Unicode normalization
        caption = unicodedata.normalize('NFKC', caption)
        
        # Remove excessive whitespace
        caption = re.sub(r'\s+', ' ', caption)
        
        # Clean up line breaks
        caption = re.sub(r'\n\s*\n', '\n\n', caption)
        
        # Trim whitespace
        caption = caption.strip()
        
        # Handle emoji normalization (keep emojis but ensure consistent representation)
        caption = self._normalize_emoji(caption)
        
        return caption
    
    def clean_comments(self, comments: Dict[str, str]) -> Dict[str, str]:
        """Clean and normalize comments."""
        cleaned_comments = {}
        
        for key, comment in comments.items():
            if isinstance(comment, str) and comment.strip():
                cleaned_comment = self.clean_caption(comment)  # Use same cleaning as caption
                if cleaned_comment:
                    cleaned_comments[key] = cleaned_comment
        
        return cleaned_comments
    
    def calculate_quality_score(self, post_data: Dict[str, Any]) -> float:
        """
        Calculate quality score for post data (0.0 to 1.0).
        
        Quality factors:
        - Username validity (0.2)
        - URL validity (0.2)
        - Caption presence and length (0.3)
        - Comments count and quality (0.3)
        """
        score = 0.0
        
        # Username score (0.2)
        username = post_data.get("usernamePost", "")
        if username and username != "unknown_user":
            if re.match(r'^[a-zA-Z0-9._]+$', username):
                score += 0.2
            else:
                score += 0.1
        
        # URL score (0.2)
        url = post_data.get("urlPost", "")
        if url and "instagram.com" in url and ("/p/" in url or "/reel/" in url):
            score += 0.2
        elif url:
            score += 0.1
        
        # Caption score (0.3)
        caption = post_data.get("caption", "")
        if caption:
            if len(caption) > 50:
                score += 0.3
            elif len(caption) > 10:
                score += 0.2
            else:
                score += 0.1
        
        # Comments score (0.3)
        comments = post_data.get("comments", {})
        if comments:
            comment_count = len(comments)
            avg_comment_length = sum(len(c) for c in comments.values()) / comment_count if comment_count > 0 else 0
            
            if comment_count >= 5 and avg_comment_length > 20:
                score += 0.3
            elif comment_count >= 3 and avg_comment_length > 10:
                score += 0.2
            elif comment_count >= 1:
                score += 0.1
        
        return min(score, 1.0)
    
    def extract_metadata(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from post data."""
        metadata = {
            "hashtags": [],
            "mentions": [],
            "urls": [],
            "emoji_count": 0,
            "word_count": 0,
            "has_location": False,
            "post_type": "unknown"
        }
        
        caption = post_data.get("caption", "")
        url = post_data.get("urlPost", "")
        
        if caption:
            # Extract hashtags
            metadata["hashtags"] = self._extract_hashtags(caption)
            
            # Extract mentions
            metadata["mentions"] = self._extract_mentions(caption)
            
            # Extract URLs
            metadata["urls"] = self._extract_urls(caption)
            
            # Count emojis
            metadata["emoji_count"] = len(emoji.emoji_list(caption))
            
            # Count words
            metadata["word_count"] = len(caption.split())
        
        # Determine post type from URL
        if "/reel/" in url:
            metadata["post_type"] = "reel"
        elif "/p/" in url:
            metadata["post_type"] = "post"
        elif "/tv/" in url:
            metadata["post_type"] = "igtv"
        
        return metadata
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from Instagram URL."""
        try:
            # Match patterns like https://www.instagram.com/username/
            match = re.search(r'instagram\.com/([^/]+)/?', url)
            if match:
                return match.group(1)
        except:
            pass
        return ""
    
    def _normalize_emoji(self, text: str) -> str:
        """Normalize emoji representation in text."""
        try:
            # Keep emojis as they are, just ensure proper encoding
            # Don't convert to text representation
            return text
        except:
            return text
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        hashtag_pattern = r'#[a-zA-Z0-9_\u00c0-\u017e\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff\u0700-\u074f\u0780-\u07bf\u1100-\u11ff\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract user mentions from text."""
        mention_pattern = r'@[a-zA-Z0-9._]+'
        mentions = re.findall(mention_pattern, text)
        return [mention.lower() for mention in mentions]
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def clean_batch_data(self, posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean a batch of post data."""
        cleaned_posts = []
        
        for i, post_data in enumerate(posts_data):
            try:
                cleaned_post = self.clean_post_data(post_data)
                cleaned_posts.append(cleaned_post)
                
                self.logger.debug(f"Cleaned post {i+1}/{len(posts_data)}")
                
            except Exception as e:
                self.logger.error(f"Error cleaning post {i+1}: {str(e)}")
                # Keep original data if cleaning fails
                cleaned_posts.append(post_data)
        
        self.logger.info(f"Cleaned {len(cleaned_posts)} posts")
        return cleaned_posts
    
    def filter_by_quality(self, posts_data: List[Dict[str, Any]], min_quality: float = 0.5) -> List[Dict[str, Any]]:
        """Filter posts by minimum quality score."""
        filtered_posts = []
        
        for post_data in posts_data:
            quality_score = post_data.get("quality_score", 0.0)
            if quality_score >= min_quality:
                filtered_posts.append(post_data)
            else:
                self.logger.debug(f"Filtered out low quality post (score: {quality_score})")
        
        self.logger.info(f"Filtered posts: {len(posts_data)} -> {len(filtered_posts)} (min quality: {min_quality})")
        return filtered_posts
    
    def get_cleaning_stats(self, original_data: List[Dict[str, Any]], cleaned_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the cleaning process."""
        stats = {
            "original_count": len(original_data),
            "cleaned_count": len(cleaned_data),
            "avg_quality_score": 0.0,
            "high_quality_count": 0,
            "metadata_extracted": 0
        }
        
        if cleaned_data:
            quality_scores = [post.get("quality_score", 0.0) for post in cleaned_data]
            stats["avg_quality_score"] = sum(quality_scores) / len(quality_scores)
            stats["high_quality_count"] = sum(1 for score in quality_scores if score >= 0.7)
            stats["metadata_extracted"] = sum(1 for post in cleaned_data if post.get("metadata"))
        
        return stats
