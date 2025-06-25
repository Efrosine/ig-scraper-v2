"""
Instagram Profile Scraper - Login Tests
Phase 1: Foundation, Login & Backup Accounts

Test suite for login functionality.
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Add core files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from utils import SessionManager, RateLimiter, setup_logging, detect_chromedriver_path
from scraper import InstagramScraper


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_load_accounts_success(self):
        """Test successful account loading."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        
        assert len(session_manager.accounts) == 2
        assert session_manager.accounts[0]["username"] == "eprosine009"
        assert session_manager.accounts[0]["password"] == "IniPwBaru123"
        assert session_manager.accounts[1]["username"] == "eprosen2"
        assert session_manager.accounts[1]["password"] == "desember@03"
    
    def test_load_accounts_empty(self):
        """Test account loading with empty environment."""
        os.environ["INSTAGRAM_ACCOUNTS"] = ""
        
        with pytest.raises(ValueError, match="No Instagram accounts found"):
            SessionManager()
    
    def test_get_current_account(self):
        """Test getting current account."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        current = session_manager.get_current_account()
        
        assert current["username"] == "eprosine009"
        assert current["password"] == "IniPwBaru123"
    
    def test_switch_to_backup_account(self):
        """Test switching to backup account."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        
        # Switch to backup
        backup = session_manager.switch_to_backup_account()
        
        assert backup["username"] == "eprosen2"
        assert backup["password"] == "desember@03"
        assert session_manager.current_account_index == 1
    
    def test_switch_beyond_available_accounts(self):
        """Test switching beyond available accounts."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123"
        
        session_manager = SessionManager()
        
        # Try to switch beyond available accounts
        backup = session_manager.switch_to_backup_account()
        
        assert backup is None
    
    def test_get_account_count(self):
        """Test getting account count."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        
        assert session_manager.get_account_count() == 2
    
    def test_get_remaining_accounts(self):
        """Test getting remaining account count."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        
        assert session_manager.get_remaining_accounts() == 1  # 2 total - 1 current
        
        session_manager.switch_to_backup_account()
        assert session_manager.get_remaining_accounts() == 0  # 2 total - 2 used
    
    def test_reset_account_index(self):
        """Test resetting account index."""
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        
        session_manager = SessionManager()
        session_manager.switch_to_backup_account()
        
        assert session_manager.current_account_index == 1
        
        session_manager.reset_account_index()
        assert session_manager.current_account_index == 0


class TestRateLimiter:
    """Test cases for RateLimiter class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        os.environ["REQUEST_DELAY"] = "3"
        os.environ["LOGIN_DELAY"] = "7"
        
        rate_limiter = RateLimiter()
        
        assert rate_limiter.request_delay == 3.0
        assert rate_limiter.login_delay == 7.0
    
    def test_rate_limiter_defaults(self):
        """Test rate limiter with default values."""
        # Clear environment variables
        os.environ.pop("REQUEST_DELAY", None)
        os.environ.pop("LOGIN_DELAY", None)
        
        rate_limiter = RateLimiter()
        
        assert rate_limiter.request_delay == 2.0
        assert rate_limiter.login_delay == 5.0
    
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_request(self, mock_time, mock_sleep):
        """Test request rate limiting."""
        # Mock time progression
        mock_time.side_effect = [0, 1, 2]  # Current time, last request, current time
        
        rate_limiter = RateLimiter()
        rate_limiter.last_request_time = 1  # Set last request time
        rate_limiter.request_delay = 2.0
        
        rate_limiter.wait_for_request()
        
        # Should sleep for 1 second (2.0 delay - 1.0 elapsed)
        mock_sleep.assert_called_once_with(1.0)


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_detect_chromedriver_path_env_var(self):
        """Test ChromeDriver detection with environment variable."""
        with patch.dict(os.environ, {"CHROMEDRIVER_PATH": "/test/chromedriver"}):
            with patch('os.path.exists', return_value=True):
                path = detect_chromedriver_path()
                assert path == "/test/chromedriver"
    
    def test_detect_chromedriver_path_common_locations(self):
        """Test ChromeDriver detection from common locations."""
        with patch.dict(os.environ, {"CHROMEDRIVER_PATH": ""}):
            with patch('os.path.exists') as mock_exists:
                # First path doesn't exist, second does
                mock_exists.side_effect = lambda path: path == "/usr/local/bin/chromedriver"
                
                path = detect_chromedriver_path()
                assert path == "/usr/local/bin/chromedriver"
    
    def test_detect_chromedriver_path_not_found(self):
        """Test ChromeDriver detection failure."""
        with patch.dict(os.environ, {"CHROMEDRIVER_PATH": ""}):
            with patch('os.path.exists', return_value=False):
                with pytest.raises(FileNotFoundError, match="ChromeDriver not found"):
                    detect_chromedriver_path()
    
    def test_setup_logging(self):
        """Test logging setup."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "LOG_TO_FILE": "false"}):
            logger = setup_logging()
            
            assert logger.name == "ig_scraper"
            assert logger.level <= 10  # DEBUG level


class TestInstagramScraper:
    """Test cases for InstagramScraper class."""
    
    @patch('utils.detect_chromedriver_path')
    @patch('selenium.webdriver.Chrome')
    def test_scraper_initialization(self, mock_chrome, mock_detect_path):
        """Test scraper initialization."""
        mock_detect_path.return_value = "/usr/bin/chromedriver"
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        scraper = InstagramScraper()
        scraper._setup_driver()
        
        assert scraper.driver == mock_driver
        mock_chrome.assert_called_once()
    
    @patch('selenium.webdriver.Chrome')
    def test_scraper_close(self, mock_chrome):
        """Test scraper cleanup."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        scraper = InstagramScraper()
        scraper.driver = mock_driver
        scraper.close()
        
        mock_driver.quit.assert_called_once()
    
    def test_scraper_context_manager(self):
        """Test scraper as context manager."""
        with patch.object(InstagramScraper, 'close') as mock_close:
            with InstagramScraper() as scraper:
                assert scraper is not None
            
            mock_close.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
