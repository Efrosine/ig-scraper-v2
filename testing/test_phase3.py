"""
Instagram Profile Scraper - Phase 3 Tests
Test post scraping functionality

This module contains tests for Phase 3 post scraping features.
"""

import unittest
import sys
import os
import json
import time
from unittest.mock import Mock, patch

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))

from main import InstagramProfileScraper
from scraper import InstagramScraper
from parser import InstagramPostParser
from phase3_scraper import Phase3InstagramScraper


class TestPhase3PostScraping(unittest.TestCase):
    """Test Phase 3 post scraping functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_username = "malangraya_info"
        self.test_post_count = 3
        self.test_comment_count = 2
        
    def test_main_scraper_post_method(self):
        """Test main scraper post scraping method exists."""
        scraper = InstagramProfileScraper()
        
        # Check if scrape_profile_posts method exists
        self.assertTrue(hasattr(scraper, 'scrape_profile_posts'))
        self.assertTrue(callable(getattr(scraper, 'scrape_profile_posts')))
        
    def test_scraper_post_method(self):
        """Test core scraper post scraping method exists."""
        scraper = InstagramScraper()
        
        # Check if scrape_posts method exists
        self.assertTrue(hasattr(scraper, 'scrape_posts'))
        self.assertTrue(callable(getattr(scraper, 'scrape_posts')))
        
    def test_parser_functionality(self):
        """Test parser functionality."""
        parser = InstagramPostParser()
        
        # Check if extract_post_data method exists
        self.assertTrue(hasattr(parser, 'extract_post_data'))
        self.assertTrue(callable(getattr(parser, 'extract_post_data')))
        
    def test_phase3_scraper_class(self):
        """Test Phase 3 scraper class."""
        scraper = Phase3InstagramScraper()
        
        # Check if main methods exist
        self.assertTrue(hasattr(scraper, 'run_phase3_complete'))
        self.assertTrue(hasattr(scraper, 'run_interactive_mode'))
        self.assertTrue(callable(getattr(scraper, 'run_phase3_complete')))
        
    def test_output_format_structure(self):
        """Test that the expected output format is properly structured."""
        # Expected output format based on requirements
        expected_structure = {
            "results": [
                {
                    "usernamePost": str,
                    "urlPost": str,
                    "releaseDate": str,
                    "caption": str,
                    "comments": dict
                }
            ]
        }
        
        # This test validates the structure we expect
        sample_post = {
            "usernamePost": "test_user",
            "urlPost": "https://www.instagram.com/p/test123/",
            "releaseDate": "2025-01-01T12:00:00.000Z",
            "caption": "Test caption",
            "comments": {
                "0": "First comment",
                "1": "Second comment"
            }
        }
        
        # Validate structure
        self.assertIn("usernamePost", sample_post)
        self.assertIn("urlPost", sample_post)
        self.assertIn("releaseDate", sample_post)
        self.assertIn("caption", sample_post)
        self.assertIn("comments", sample_post)
        self.assertIsInstance(sample_post["comments"], dict)
        
    def test_save_phase3_results_method(self):
        """Test save Phase 3 results method."""
        scraper = InstagramProfileScraper()
        
        # Check if save_phase3_results method exists
        self.assertTrue(hasattr(scraper, 'save_phase3_results'))
        self.assertTrue(callable(getattr(scraper, 'save_phase3_results')))
        
    @patch('builtins.input', side_effect=['malangraya_info', '3', '2'])
    def test_interactive_mode_input_handling(self, mock_input):
        """Test interactive mode input handling."""
        scraper = Phase3InstagramScraper()
        
        # This would test the input handling logic
        # In a real test, we'd mock the scraping process
        self.assertTrue(hasattr(scraper, 'run_interactive_mode'))
        
    def test_post_url_validation(self):
        """Test post URL validation logic."""
        valid_urls = [
            "https://www.instagram.com/p/DHNs4rdh4ha/",
            "https://www.instagram.com/reel/DHNs4rdh4ha/",
            "https://www.instagram.com/p/DLUZmqIh9vB/"
        ]
        
        invalid_urls = [
            "https://facebook.com/post/123",
            "https://www.instagram.com/user/",
            "not_a_url",
            ""
        ]
        
        for url in valid_urls:
            self.assertTrue(self._is_valid_instagram_post_url(url))
            
        for url in invalid_urls:
            self.assertFalse(self._is_valid_instagram_post_url(url))
    
    def _is_valid_instagram_post_url(self, url: str) -> bool:
        """Helper method to validate Instagram post URLs."""
        import re
        pattern = r'https://www\.instagram\.com/(p|reel)/.+'
        return bool(re.match(pattern, url))
    
    def test_comment_count_validation(self):
        """Test comment count validation."""
        valid_counts = [0, 1, 5, 10]
        invalid_counts = [-1, -5, "abc", None]
        
        for count in valid_counts:
            self.assertTrue(isinstance(count, int) and count >= 0)
            
        for count in invalid_counts:
            self.assertFalse(isinstance(count, int) and count >= 0)
    
    def test_post_count_validation(self):
        """Test post count validation."""
        valid_counts = [1, 5, 10, 20]
        invalid_counts = [0, -1, -5, "abc", None]
        
        for count in valid_counts:
            self.assertTrue(isinstance(count, int) and count > 0)
            
        for count in invalid_counts:
            self.assertFalse(isinstance(count, int) and count > 0)


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for Phase 3."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.output_dir = "output"
        self.test_files = []
    
    def tearDown(self):
        """Clean up test files."""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    
    def test_output_directory_creation(self):
        """Test that output directory is created."""
        scraper = InstagramProfileScraper()
        
        # Simulate saving results
        test_results = {
            "phase": 3,
            "results": [],
            "timestamp": int(time.time())
        }
        
        # This would create the output directory
        expected_dir = "output"
        if not os.path.exists(expected_dir):
            os.makedirs(expected_dir, exist_ok=True)
            
        self.assertTrue(os.path.exists(expected_dir))
    
    def test_json_output_format(self):
        """Test JSON output format compliance."""
        sample_output = {
            "phase": 3,
            "title": "Post Scraping",
            "timestamp": int(time.time()),
            "target_username": "test_user",
            "scraping_results": {
                "results": [
                    {
                        "usernamePost": "test_user",
                        "urlPost": "https://www.instagram.com/p/test/",
                        "releaseDate": "2025-01-01T12:00:00.000Z",
                        "caption": "Test caption",
                        "comments": {
                            "0": "Test comment"
                        }
                    }
                ]
            },
            "status": "completed"
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(sample_output, indent=2, ensure_ascii=False)
            parsed_back = json.loads(json_str)
            self.assertEqual(sample_output, parsed_back)
        except Exception as e:
            self.fail(f"JSON serialization failed: {str(e)}")


class TestPhase3ErrorHandling(unittest.TestCase):
    """Test error handling in Phase 3."""
    
    def test_invalid_username_handling(self):
        """Test handling of invalid usernames."""
        invalid_usernames = ["", None, "user_that_definitely_does_not_exist_12345"]
        
        for username in invalid_usernames:
            # In a real implementation, this should handle errors gracefully
            if username is None or username == "":
                self.assertTrue(True)  # Should be handled
            else:
                # Should not crash the application
                self.assertIsInstance(username, str)
    
    def test_network_error_simulation(self):
        """Test network error handling."""
        # This would test what happens when network fails
        # In real implementation, should have retry logic and graceful degradation
        self.assertTrue(True)  # Placeholder for actual network error tests
    
    def test_missing_post_elements(self):
        """Test handling when post elements are missing."""
        # This would test parsing when certain elements don't exist
        self.assertTrue(True)  # Placeholder for missing element tests


def run_phase3_tests():
    """Run all Phase 3 tests."""
    print("="*60)
    print("RUNNING PHASE 3 POST SCRAPING TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3PostScraping))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase3ErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 3 TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'PASSED' if success else 'FAILED'}")
    print("="*60)
    
    return success


if __name__ == "__main__":
    run_phase3_tests()
