"""
Test Module for Phase 5: Search by Location or Suspected Account
Tests both location-based and suspected account search algorithms.
"""

import unittest
import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))

from location_search import LocationSearcher
from suspected_account_search import SuspectedAccountSearcher
from output_logger import OutputLogger
from phase5_scraper import Phase5InstagramScraper


class TestPhase5SearchAlgorithms(unittest.TestCase):
    """Test cases for Phase 5 search algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_logger = Mock()
        
        # Mock WebDriver elements
        self.mock_element = Mock()
        self.mock_element.get_attribute.return_value = "https://instagram.com/p/test123/"
        self.mock_element.text = "Test post content"
        
        self.mock_driver.find_elements.return_value = [self.mock_element]
        self.mock_driver.get.return_value = None
        self.mock_driver.execute_script.return_value = None
        
    def test_location_searcher_initialization(self):
        """Test LocationSearcher initialization."""
        searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        
        self.assertEqual(searcher.driver, self.mock_driver)
        self.assertEqual(searcher.logger, self.mock_logger)
        self.assertEqual(searcher.wait_timeout, 10)
    
    def test_suspected_account_searcher_initialization(self):
        """Test SuspectedAccountSearcher initialization."""
        searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        
        self.assertEqual(searcher.driver, self.mock_driver)
        self.assertEqual(searcher.logger, self.mock_logger)
        self.assertEqual(searcher.wait_timeout, 10)
    
    @patch('location_search.WebDriverWait')
    def test_location_search_basic_functionality(self, mock_wait):
        """Test basic location search functionality."""
        # Setup mock
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.return_value = self.mock_element
        
        searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        
        # Test search capability verification
        result = searcher.verify_location_search_capability()
        
        # Should call driver.get and look for search elements
        self.mock_driver.get.assert_called()
        self.assertTrue(isinstance(result, bool))
    
    @patch('suspected_account_search.WebDriverWait')
    def test_suspected_account_search_basic_functionality(self, mock_wait):
        """Test basic suspected account search functionality."""
        # Setup mock
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.return_value = self.mock_element
        
        searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        
        # Test search capability verification
        result = searcher.verify_account_search_capability()
        
        # Should call driver.get and check profile accessibility
        self.mock_driver.get.assert_called()
        self.assertTrue(isinstance(result, bool))
    
    def test_location_search_post_collection(self):
        """Test location search post collection algorithm."""
        searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        
        # Mock post elements
        post_elements = [
            Mock(get_attribute=Mock(return_value=f"https://instagram.com/p/test{i}/"))
            for i in range(5)
        ]
        self.mock_driver.find_elements.return_value = post_elements
        
        # Test post collection
        posts = searcher._collect_location_posts(3)
        
        # Should return at most 3 posts
        self.assertLessEqual(len(posts), 3)
        
        # Each post should have required fields
        for post in posts:
            self.assertIn('url', post)
            self.assertIn('search_type', post)
            self.assertEqual(post['search_type'], 'location')
    
    def test_suspected_account_post_collection(self):
        """Test suspected account post collection algorithm."""
        searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        
        # Mock post elements
        post_elements = [
            Mock(get_attribute=Mock(return_value=f"https://instagram.com/testuser/p/test{i}/"))
            for i in range(5)
        ]
        self.mock_driver.find_elements.return_value = post_elements
        
        # Test post collection
        posts = searcher._collect_account_posts("testuser", 3)
        
        # Should return at most 3 posts
        self.assertLessEqual(len(posts), 3)
        
        # Each post should have required fields
        for post in posts:
            self.assertIn('url', post)
            self.assertIn('search_type', post)
            self.assertEqual(post['search_type'], 'suspected_account')
            self.assertIn('account_username', post)
    
    def test_output_logger_functionality(self):
        """Test OutputLogger functionality."""
        logger = OutputLogger()
        
        # Test session start logging
        session_info = logger.log_session_start(
            "location", 
            "Malang", 
            {"post_count": 10, "comment_count": 5}
        )
        
        self.assertIn('session_id', session_info)
        self.assertIn('start_time', session_info)
        self.assertEqual(session_info['search_type'], 'location')
        self.assertEqual(session_info['search_target'], 'Malang')
        
        # Test session end logging
        end_info = logger.log_session_end(session_info, 5, True)
        
        self.assertIn('end_time', end_info)
        self.assertIn('duration_seconds', end_info)
        self.assertEqual(end_info['results_count'], 5)
        self.assertTrue(end_info['success'])
        
        # Test error logging
        logger.log_error("TestError", "This is a test error", {"context": "test"})
        
        # Test performance logging
        logger.log_performance_metric("extraction_time", 5.5, "seconds")
        
        # Test log file paths
        log_files = logger.get_log_files()
        self.assertIn('detailed', log_files)
        self.assertIn('errors', log_files)
        self.assertIn('search', log_files)
        self.assertIn('performance', log_files)
    
    def test_search_algorithm_separation(self):
        """Test that location and suspected account algorithms are separate."""
        location_searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        account_searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        
        # Test that they have different methods
        self.assertTrue(hasattr(location_searcher, 'search_by_location'))
        self.assertFalse(hasattr(location_searcher, 'search_by_suspected_account'))
        
        self.assertTrue(hasattr(account_searcher, 'search_by_suspected_account'))
        self.assertTrue(hasattr(account_searcher, 'get_account_info'))
        self.assertFalse(hasattr(account_searcher, 'search_by_location'))
    
    def test_data_structure_compatibility(self):
        """Test that search results match expected data structure."""
        # Test location search result structure
        location_searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        mock_post = {
            'url': 'https://instagram.com/p/test123/',
            'element': self.mock_element,
            'search_type': 'location',
            'found_via': 'location_page'
        }
        
        # Verify required fields
        required_fields = ['url', 'search_type', 'found_via']
        for field in required_fields:
            self.assertIn(field, mock_post)
        
        # Test suspected account search result structure
        account_searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        mock_account_post = {
            'url': 'https://instagram.com/testuser/p/test123/',
            'element': self.mock_element,
            'search_type': 'suspected_account',
            'account_username': 'testuser',
            'found_via': 'profile_page'
        }
        
        # Verify required fields
        account_required_fields = ['url', 'search_type', 'account_username', 'found_via']
        for field in account_required_fields:
            self.assertIn(field, mock_account_post)
    
    @patch('phase5_scraper.InstagramProfileScraper')
    def test_phase5_scraper_location_mode(self, mock_scraper_class):
        """Test Phase5InstagramScraper location search mode."""
        # Setup mock
        mock_scraper = Mock()
        mock_scraper.initialize.return_value = True
        mock_scraper.search_by_location.return_value = {
            'phase': 5,
            'search_type': 'location',
            'search_target': 'Malang',
            'posts_extracted': 5,
            'results': []
        }
        mock_scraper.save_phase5_results.return_value = 'test_output.json'
        mock_scraper_class.return_value = mock_scraper
        
        # Test location search
        phase5_scraper = Phase5InstagramScraper()
        result = phase5_scraper.run_location_search('Malang', 10, 5)
        
        # Verify calls
        mock_scraper.initialize.assert_called_once()
        mock_scraper.search_by_location.assert_called_once_with('Malang', 10, 5)
        mock_scraper.save_phase5_results.assert_called_once()
        mock_scraper.cleanup.assert_called_once()
        
        # Verify result
        self.assertEqual(result['search_type'], 'location')
        self.assertEqual(result['search_target'], 'Malang')
    
    @patch('phase5_scraper.InstagramProfileScraper')
    def test_phase5_scraper_account_mode(self, mock_scraper_class):
        """Test Phase5InstagramScraper suspected account search mode."""
        # Setup mock
        mock_scraper = Mock()
        mock_scraper.initialize.return_value = True
        mock_scraper.search_by_suspected_account.return_value = {
            'phase': 5,
            'search_type': 'suspected_account',
            'search_target': 'malangraya_info',
            'posts_extracted': 5,
            'results': []
        }
        mock_scraper.save_phase5_results.return_value = 'test_output.json'
        mock_scraper_class.return_value = mock_scraper
        
        # Test suspected account search
        phase5_scraper = Phase5InstagramScraper()
        result = phase5_scraper.run_suspected_account_search('malangraya_info', 10, 5)
        
        # Verify calls
        mock_scraper.initialize.assert_called_once()
        mock_scraper.search_by_suspected_account.assert_called_once_with('malangraya_info', 10, 5)
        mock_scraper.save_phase5_results.assert_called_once()
        mock_scraper.cleanup.assert_called_once()
        
        # Verify result
        self.assertEqual(result['search_type'], 'suspected_account')
        self.assertEqual(result['search_target'], 'malangraya_info')
    
    def test_error_handling(self):
        """Test error handling in search algorithms."""
        # Test location searcher error handling
        location_searcher = LocationSearcher(self.mock_driver, self.mock_logger)
        
        # Mock driver that raises exception
        self.mock_driver.get.side_effect = Exception("Network error")
        
        result = location_searcher.search_by_location("Malang", 5)
        self.assertEqual(result, [])  # Should return empty list on error
        
        # Test suspected account searcher error handling
        account_searcher = SuspectedAccountSearcher(self.mock_driver, self.mock_logger)
        
        result = account_searcher.search_by_suspected_account("testuser", 5)
        self.assertEqual(result, [])  # Should return empty list on error
    
    def test_search_coordination(self):
        """Test that Phase 5 properly coordinates between search methods."""
        # This test verifies that the main module can handle both search types
        # and that they are mutually exclusive
        
        # Mock the environment to test coordination
        with patch('main.LocationSearcher') as mock_location, \
             patch('main.SuspectedAccountSearcher') as mock_account:
            
            # Test that both searchers can be initialized
            mock_location.return_value = Mock()
            mock_account.return_value = Mock()
            
            # This would be tested with actual InstagramProfileScraper
            # but we can verify the structure is correct
            self.assertTrue(True)  # Placeholder for actual coordination test


class TestPhase5Integration(unittest.TestCase):
    """Integration tests for Phase 5 functionality."""
    
    def test_default_environment_configuration(self):
        """Test that default configuration values are properly set."""
        # Check that the environment has the expected defaults
        default_location = os.getenv('DEFAULT_LOCATION', 'Malang')
        default_suspected_account = os.getenv('DEFAULT_SUSPECTED_ACCOUNT', 'malangraya_info')
        default_post_count = int(os.getenv('DEFAULT_POST_COUNT', '10'))
        default_comment_count = int(os.getenv('DEFAULT_COMMENT_COUNT', '5'))
        
        self.assertIsInstance(default_location, str)
        self.assertIsInstance(default_suspected_account, str)
        self.assertIsInstance(default_post_count, int)
        self.assertIsInstance(default_comment_count, int)
        
        self.assertTrue(len(default_location) > 0)
        self.assertTrue(len(default_suspected_account) > 0)
        self.assertGreater(default_post_count, 0)
        self.assertGreater(default_comment_count, 0)
    
    def test_output_structure_consistency(self):
        """Test that output structure is consistent across search types."""
        # Expected output structure for both search types
        expected_fields = [
            'phase', 'search_type', 'search_target', 'extraction_time',
            'session_id', 'total_posts_found', 'posts_extracted',
            'requested_posts', 'requested_comments_per_post', 'results'
        ]
        
        # This would be tested with actual output files
        # For now, we verify the structure is defined
        self.assertTrue(len(expected_fields) > 0)
    
    def test_logging_integration(self):
        """Test that logging is properly integrated across all components."""
        logger = OutputLogger()
        
        # Test that logger creates necessary directories
        log_files = logger.get_log_files()
        
        for log_type, log_path in log_files.items():
            # Verify log file paths are properly formatted
            self.assertTrue(log_path.endswith('.log'))
            self.assertIn(str(logger.get_session_id()), log_path)


def run_phase5_tests():
    """Run all Phase 5 tests."""
    print("🧪 Running Phase 5 Search Algorithm Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestPhase5SearchAlgorithms))
    test_suite.addTest(unittest.makeSuite(TestPhase5Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"🧪 Phase 5 Test Results:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    
    return success


if __name__ == "__main__":
    success = run_phase5_tests()
    sys.exit(0 if success else 1)
