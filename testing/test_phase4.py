#!/usr/bin/env python3
"""
Phase 4 Testing - Advanced Parsing & Cleaning
Tests for enhanced BeautifulSoup parsing, data cleaning, and quality scoring
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from data_cleaner import DataCleaner
from parser import InstagramPostParser
from main import InstagramProfileScraper


class TestPhase4DataCleaner(unittest.TestCase):
    """Test Phase 4 data cleaning functionality."""
    
    def setUp(self):
        self.cleaner = DataCleaner()
        
    def test_clean_username(self):
        """Test username cleaning."""
        # Test cases
        test_cases = [
            ("test_user", "test_user"),
            ("@test_user", "test_user"),
            ("https://instagram.com/test_user/", "test_user"),
            ("test_user@#$%", "test_user"),
            ("", "unknown_user"),
            (None, "unknown_user")
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = self.cleaner.clean_username(input_val)
                self.assertEqual(result, expected)
    
    def test_clean_caption(self):
        """Test caption cleaning."""
        # Test HTML entities
        caption_html = "This is a &quot;test&quot; caption with &amp; symbols"
        cleaned = self.cleaner.clean_caption(caption_html)
        self.assertIn('"test"', cleaned)
        self.assertIn('&', cleaned)
        
        # Test whitespace normalization
        caption_whitespace = "This   has    multiple   spaces\n\n\n\nand   lines"
        cleaned = self.cleaner.clean_caption(caption_whitespace)
        self.assertNotIn('   ', cleaned)  # Should not have multiple spaces
        
    def test_quality_scoring(self):
        """Test quality scoring algorithm."""
        # High quality post
        high_quality_post = {
            "usernamePost": "valid_user",
            "urlPost": "https://www.instagram.com/p/ABC123/",
            "caption": "This is a detailed caption with more than 50 characters to test quality scoring",
            "comments": {
                "0": "Great post! This is a meaningful comment.",
                "1": "I totally agree with this perspective.",
                "2": "Thanks for sharing this valuable content."
            }
        }
        
        score = self.cleaner.calculate_quality_score(high_quality_post)
        self.assertGreater(score, 0.5)
        
        # Low quality post
        low_quality_post = {
            "usernamePost": "unknown_user",
            "urlPost": "",
            "caption": "short",
            "comments": {}
        }
        
        score = self.cleaner.calculate_quality_score(low_quality_post)
        self.assertLess(score, 0.5)
    
    def test_metadata_extraction(self):
        """Test metadata extraction from posts."""
        post_data = {
            "caption": "Check out this #amazing #sunset at @location_name! 🌅 Visit https://example.com for more",
            "urlPost": "https://www.instagram.com/p/ABC123/"
        }
        
        metadata = self.cleaner.extract_metadata(post_data)
        
        # Test hashtag extraction
        self.assertIn('#amazing', metadata['hashtags'])
        self.assertIn('#sunset', metadata['hashtags'])
        
        # Test mention extraction
        self.assertIn('@location_name', metadata['mentions'])
        
        # Test URL extraction
        self.assertIn('https://example.com', metadata['urls'])
        
        # Test post type detection
        self.assertEqual(metadata['post_type'], 'post')
        
    def test_emoji_handling(self):
        """Test emoji normalization."""
        text_with_emoji = "Great post! 😍🔥👍 Love it!"
        cleaned = self.cleaner.clean_caption(text_with_emoji)
        
        # Should preserve emojis but normalize them
        self.assertIn('😍', cleaned)
        self.assertIn('🔥', cleaned)
        self.assertIn('👍', cleaned)


class TestPhase4Parser(unittest.TestCase):
    """Test Phase 4 enhanced parsing functionality."""
    
    def setUp(self):
        self.parser = InstagramPostParser()
        
    @patch('selenium.webdriver.Chrome')
    def test_enhanced_parsing_initialization(self, mock_driver):
        """Test enhanced parser initialization."""
        self.assertIsNotNone(self.parser.data_cleaner)
        self.assertIsInstance(self.parser.data_cleaner, DataCleaner)
        
    def test_caption_filtering(self):
        """Test caption likelihood filtering."""
        # Likely captions
        good_captions = [
            "This is a real caption with substance",
            "Check out this amazing view! #sunset",
            "Had a great day with friends 😊"
        ]
        
        for caption in good_captions:
            with self.subTest(caption=caption):
                result = self.parser._is_likely_caption(caption)
                self.assertTrue(result)
        
        # Non-captions
        bad_captions = [
            "Like",
            "123",
            "View",
            "•",
            "@user"
        ]
        
        for caption in bad_captions:
            with self.subTest(caption=caption):
                result = self.parser._is_likely_caption(caption)
                self.assertFalse(result)
    
    def test_comment_filtering(self):
        """Test comment likelihood filtering."""
        # Likely comments
        good_comments = [
            "Great post! Love it",
            "This is so inspiring",
            "Thanks for sharing this"
        ]
        
        for comment in good_comments:
            with self.subTest(comment=comment):
                result = self.parser._is_likely_comment(comment)
                self.assertTrue(result)
        
        # Non-comments
        bad_comments = [
            "Like",
            "Reply",
            "5m",
            "❤️",
            "View replies"
        ]
        
        for comment in bad_comments:
            with self.subTest(comment=comment):
                result = self.parser._is_likely_comment(comment)
                self.assertFalse(result)


class TestPhase4Integration(unittest.TestCase):
    """Test Phase 4 integration and main functionality."""
    
    def setUp(self):
        self.scraper = InstagramProfileScraper()
        
    def test_phase4_initialization(self):
        """Test Phase 4 specific initialization."""
        # Mock the scraper initialization
        with patch.object(self.scraper, 'scraper') as mock_scraper:
            mock_scraper.login_with_backup_support.return_value = True
            mock_scraper.session_manager.get_current_account.return_value = {'username': 'test_user'}
            mock_scraper.session_manager.get_account_count.return_value = 2
            mock_scraper.session_manager.get_remaining_accounts.return_value = 1
            
            result = self.scraper.initialize()
            
            # Should have Phase 4 components
            self.assertIsNotNone(self.scraper.parser)
            self.assertIsNotNone(self.scraper.data_cleaner)
            self.assertIn("phase", self.scraper.session_data)
            self.assertEqual(self.scraper.session_data["phase"], "4")
            
    def test_enhanced_post_scraping_parameters(self):
        """Test enhanced post scraping method parameters."""
        # Test method exists and has correct signature
        self.assertTrue(hasattr(self.scraper, 'scrape_posts_enhanced'))
        
        # Test method parameters
        import inspect
        sig = inspect.signature(self.scraper.scrape_posts_enhanced)
        params = list(sig.parameters.keys())
        
        expected_params = ['username', 'post_count', 'comment_count', 'min_quality']
        for param in expected_params:
            self.assertIn(param, params)


class TestPhase4QualityScoring(unittest.TestCase):
    """Test Phase 4 quality scoring system."""
    
    def setUp(self):
        self.cleaner = DataCleaner()
        
    def test_quality_score_components(self):
        """Test individual quality score components."""
        # Perfect post
        perfect_post = {
            "usernamePost": "perfect_user",
            "urlPost": "https://www.instagram.com/p/ABC123/",
            "caption": "This is an excellent caption with more than 50 characters and meaningful content that should score high",
            "comments": {
                "0": "Amazing post! Really enjoyed reading this content.",
                "1": "Thanks for sharing such valuable insights.",
                "2": "This is exactly what I was looking for.",
                "3": "Great work on this detailed explanation.",
                "4": "Love the way you explained this concept."
            }
        }
        
        score = self.cleaner.calculate_quality_score(perfect_post)
        self.assertGreater(score, 0.8)  # Should be high quality
        
        # Test score breakdown
        # Username (valid) = 0.2
        # URL (valid Instagram) = 0.2  
        # Caption (>50 chars) = 0.3
        # Comments (5 comments, good length) = 0.3
        # Total should be close to 1.0
        
    def test_quality_filtering(self):
        """Test quality-based filtering."""
        posts = [
            {
                "usernamePost": "high_quality_user",
                "urlPost": "https://www.instagram.com/p/ABC123/",
                "caption": "High quality caption with substantial content",
                "comments": {"0": "Great comment", "1": "Another good comment"}
            },
            {
                "usernamePost": "unknown_user",
                "urlPost": "",
                "caption": "low",
                "comments": {}
            }
        ]
        
        # Clean and score posts
        cleaned_posts = []
        for post in posts:
            cleaned = self.cleaner.clean_post_data(post)
            cleaned_posts.append(cleaned)
        
        # Filter by quality
        high_quality_posts = self.cleaner.filter_by_quality(cleaned_posts, min_quality=0.5)
        
        # Should filter out low quality posts
        self.assertLess(len(high_quality_posts), len(cleaned_posts))
        
        # Remaining posts should have quality >= 0.5
        for post in high_quality_posts:
            self.assertGreaterEqual(post.get('quality_score', 0), 0.5)


def run_phase4_tests():
    """Run all Phase 4 tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPhase4DataCleaner,
        TestPhase4Parser,
        TestPhase4Integration,
        TestPhase4QualityScoring
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running Phase 4 Tests: Advanced Parsing & Cleaning")
    print("=" * 60)
    
    success = run_phase4_tests()
    
    if success:
        print("\n✅ All Phase 4 tests passed!")
    else:
        print("\n❌ Some Phase 4 tests failed!")
        sys.exit(1)
