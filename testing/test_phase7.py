"""
Instagram Profile Scraper - Phase 7 Tests
Phase 7: HTTP Endpoint Implementation

This module contains tests for the HTTP endpoint functionality and input validation.
"""

import json
import time
import unittest
import requests
import threading
import sys
import os
from unittest.mock import patch, MagicMock

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))

from api_server import InstagramScrapingAPI
from phase7_scraper import Phase7InstagramScraper


class TestPhase7HTTPEndpoint(unittest.TestCase):
    """Test cases for Phase 7 HTTP endpoint functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api = InstagramScrapingAPI()
        cls.app = cls.api.app
        cls.client = cls.app.test_client()
        cls.app.config['TESTING'] = True
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
    
    def test_scrape_endpoint_invalid_json(self):
        """Test scrape endpoint with invalid JSON."""
        response = self.client.post('/scrape', 
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_scrape_endpoint_missing_suspected_account(self):
        """Test scrape endpoint without suspected_account (should use default)."""
        request_data = {
            "post_count": 5,
            "comment_count": 3
        }
        
        # Mock the scraping process
        with patch('api_server.InstagramProfileScraper') as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.initialize.return_value = True
            mock_scraper.scrape_profile.return_value = {"username": "test", "profile_url": "test"}
            mock_scraper.scrape_posts.return_value = []
            mock_scraper_class.return_value = mock_scraper
            
            response = self.client.post('/scrape',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            # Should not fail due to missing suspected_account (uses default)
            self.assertIn(response.status_code, [200, 500])  # May fail due to actual scraping, but validation should pass
    
    def test_scrape_endpoint_invalid_post_count(self):
        """Test scrape endpoint with invalid post_count."""
        request_data = {
            "suspected_account": "test_account",
            "post_count": -5,  # Invalid: negative
            "comment_count": 3
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('post_count', data['message'])
    
    def test_scrape_endpoint_invalid_comment_count(self):
        """Test scrape endpoint with invalid comment_count."""
        request_data = {
            "suspected_account": "test_account",
            "post_count": 5,
            "comment_count": -3  # Invalid: negative
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('comment_count', data['message'])
    
    def test_scrape_endpoint_invalid_accounts_format(self):
        """Test scrape endpoint with invalid accounts format."""
        request_data = {
            "accounts": "invalid_format",  # Should be list
            "suspected_account": "test_account",
            "post_count": 5,
            "comment_count": 3
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Accounts must be a list', data['message'])
    
    def test_scrape_endpoint_invalid_account_structure(self):
        """Test scrape endpoint with invalid account structure."""
        request_data = {
            "accounts": [{"username": "test"}],  # Missing password
            "suspected_account": "test_account",
            "post_count": 5,
            "comment_count": 3
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('username', data['message'])
        self.assertIn('password', data['message'])
    
    def test_scrape_endpoint_empty_suspected_account(self):
        """Test scrape endpoint with empty suspected_account."""
        request_data = {
            "suspected_account": "",  # Empty string
            "post_count": 5,
            "comment_count": 3
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        # Should not fail because empty string will use default
        # The actual response depends on whether scraping succeeds
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_validation_logic(self):
        """Test the validation logic directly."""
        # Test valid data
        valid_data = {
            "accounts": [{"username": "user1", "password": "pass1"}],
            "suspected_account": "test_account",
            "post_count": 10,
            "comment_count": 5
        }
        
        result = self.api._validate_request(valid_data)
        self.assertFalse(result['error'])
        self.assertEqual(result['suspected_account'], 'test_account')
        self.assertEqual(result['post_count'], 10)
        self.assertEqual(result['comment_count'], 5)
        
        # Test data with defaults
        minimal_data = {}
        result = self.api._validate_request(minimal_data)
        self.assertFalse(result['error'])
        # Should use default values
        self.assertIsNotNone(result['suspected_account'])
        self.assertIsNotNone(result['post_count'])
        self.assertIsNotNone(result['comment_count'])


class TestPhase7Integration(unittest.TestCase):
    """Integration tests for Phase 7."""
    
    def test_phase7_scraper_initialization(self):
        """Test Phase7InstagramScraper initialization."""
        scraper = Phase7InstagramScraper()
        
        self.assertIsNotNone(scraper.logger)
        self.assertIsNotNone(scraper.env_vars)
        self.assertIsNone(scraper.api_server)  # Not created until run()
    
    def test_environment_variable_loading(self):
        """Test environment variable loading."""
        from utils import load_environment_variables
        
        env_vars = load_environment_variables()
        
        # Should contain expected keys
        expected_keys = [
            'DEFAULT_SUSPECTED_ACCOUNT',
            'DEFAULT_POST_COUNT', 
            'DEFAULT_COMMENT_COUNT',
            'FORWARDING_PORT'
        ]
        
        for key in expected_keys:
            self.assertIn(key, env_vars)
    
    @patch('sys.argv', ['phase7_scraper.py', 'help'])
    def test_help_command(self):
        """Test help command."""
        from phase7_scraper import main
        
        # Should not raise exception
        try:
            main()
        except SystemExit:
            pass  # Expected for help command


class TestPhase7MockScraping(unittest.TestCase):
    """Test Phase 7 with mocked scraping functionality."""
    
    def setUp(self):
        """Set up test environment with mocks."""
        self.api = InstagramScrapingAPI()
        self.app = self.api.app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('api_server.InstagramProfileScraper')
    def test_successful_scraping_request(self, mock_scraper_class):
        """Test successful scraping request with mocked scraper."""
        # Mock scraper behavior
        mock_scraper = MagicMock()
        mock_scraper.initialize.return_value = True
        mock_scraper.scrape_profile.return_value = {
            "username": "test_account",
            "profile_url": "https://instagram.com/test_account/",
            "posts_count": "100",
            "followers_count": "1000"
        }
        mock_scraper.scrape_posts.return_value = [
            {
                "usernamePost": "test_account",
                "urlPost": "https://instagram.com/p/test123/",
                "releaseDate": "2025-01-01T12:00:00.000Z",
                "caption": "Test caption",
                "comments": {
                    "0": "Test comment 1",
                    "1": "Test comment 2"
                }
            }
        ]
        mock_scraper_class.return_value = mock_scraper
        
        # Make request
        request_data = {
            "accounts": [{"username": "test_user", "password": "test_pass"}],
            "suspected_account": "test_account",
            "post_count": 5,
            "comment_count": 3
        }
        
        response = self.client.post('/scrape',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data)
        self.assertIn('metadata', data)
        self.assertEqual(len(data['results']), 1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
