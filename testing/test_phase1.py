"""
Instagram Profile Scraper - Phase 1 Tests
Phase 1: Foundation, Login & Backup Accounts

Comprehensive test suite for Phase 1 functionality.
"""

import pytest
import sys
import os
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add core files to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))

from main import InstagramProfileScraper
from phase1_scraper import Phase1InstagramScraper


class TestPhase1Integration:
    """Integration tests for Phase 1 functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up test environment variables using real credentials from .env
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        os.environ["LOG_TO_FILE"] = "false"  # Disable file logging for tests
        
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('scraper.InstagramScraper._setup_driver')
    @patch('scraper.InstagramScraper.login_with_backup_support')
    def test_phase1_scraper_initialization(self, mock_login, mock_setup):
        """Test Phase 1 scraper initialization."""
        mock_login.return_value = True
        
        scraper = InstagramProfileScraper()
        result = scraper.initialize()
        
        assert result is True
        assert scraper.session_data is not None
        assert "current_account" in scraper.session_data
    
    @patch('scraper.InstagramScraper._setup_driver')
    @patch('scraper.InstagramScraper.login_with_backup_support')
    def test_phase1_scraper_initialization_failure(self, mock_login, mock_setup):
        """Test Phase 1 scraper initialization failure."""
        mock_login.return_value = False
        
        scraper = InstagramProfileScraper()
        result = scraper.initialize()
        
        assert result is False
    
    def test_session_info_structure(self):
        """Test session info structure."""
        with patch('scraper.InstagramScraper._setup_driver'):
            with patch('scraper.InstagramScraper.login_with_backup_support', return_value=True):
                scraper = InstagramProfileScraper()
                scraper.initialize()
                
                session_info = scraper.get_session_info()
                
                assert "session_data" in session_info
                assert "status" in session_info
                assert "timestamp" in session_info
                assert session_info["status"] == "active"
    
    @patch('scraper.InstagramScraper._setup_driver')
    @patch('scraper.InstagramScraper.login_with_backup_support')
    def test_basic_navigation_test(self, mock_login, mock_setup):
        """Test basic navigation functionality."""
        mock_login.return_value = True
        
        # Create a mock driver
        mock_driver = Mock()
        mock_driver.current_url = "https://www.instagram.com/"
        mock_driver.get = Mock()
        
        scraper = InstagramProfileScraper()
        scraper.initialize()
        
        # Manually set the driver after initialization
        scraper.scraper.driver = mock_driver
        
        with patch.object(scraper.scraper, 'take_screenshot'):
            result = scraper.test_basic_navigation()
        
        assert result is True
        mock_driver.get.assert_called_with("https://www.instagram.com/")
    
    @patch('scraper.InstagramScraper._setup_driver')
    @patch('scraper.InstagramScraper.login_with_backup_support')
    def test_basic_navigation_test_login_redirect(self, mock_login, mock_setup):
        """Test basic navigation with login redirect."""
        mock_login.return_value = True
        
        # Create a mock driver
        mock_driver = Mock()
        mock_driver.current_url = "https://www.instagram.com/accounts/login/"
        mock_driver.get = Mock()
        
        scraper = InstagramProfileScraper()
        scraper.initialize()
        
        # Manually set the driver after initialization
        scraper.scraper.driver = mock_driver
        
        with patch.object(scraper.scraper, 'take_screenshot'):
            result = scraper.test_basic_navigation()
        
        assert result is False
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    @patch('os.makedirs')
    def test_save_phase1_results(self, mock_makedirs, mock_json_dump, mock_open):
        """Test saving Phase 1 results."""
        with patch('scraper.InstagramScraper._setup_driver'):
            with patch('scraper.InstagramScraper.login_with_backup_support', return_value=True):
                scraper = InstagramProfileScraper()
                scraper.initialize()
                
                result_file = scraper.save_phase1_results()
                
                assert result_file == "output/phase1_results.json"
                mock_makedirs.assert_called_with("output", exist_ok=True)
                assert mock_json_dump.call_count == 2  # Main file + backup


class TestPhase1ScraperClass:
    """Tests for Phase1InstagramScraper class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        os.environ["LOG_TO_FILE"] = "false"
    
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_phase1_scraper_initialization(self):
        """Test Phase1InstagramScraper initialization."""
        scraper = Phase1InstagramScraper()
        
        assert scraper.logger is not None
        assert scraper.scraper is None
    
    @patch('os.path.exists')
    def test_environment_setup_success(self, mock_exists):
        """Test successful environment setup test."""
        mock_exists.return_value = True
        
        with patch('utils.detect_chromedriver_path', return_value="/usr/bin/chromedriver"):
            scraper = Phase1InstagramScraper()
            result = scraper.test_environment_setup()
        
        assert result is True
    
    @patch('os.path.exists')
    def test_environment_setup_missing_env_file(self, mock_exists):
        """Test environment setup with missing .env file."""
        def exists_side_effect(path):
            return not path.endswith(".env")
        
        mock_exists.side_effect = exists_side_effect
        
        scraper = Phase1InstagramScraper()
        result = scraper.test_environment_setup()
        
        assert result is False
    
    @patch('os.path.exists')
    def test_environment_setup_missing_requirements(self, mock_exists):
        """Test environment setup with missing requirements.txt."""
        def exists_side_effect(path):
            return not path.endswith("requirements.txt")
        
        mock_exists.side_effect = exists_side_effect
        
        scraper = Phase1InstagramScraper()
        result = scraper.test_environment_setup()
        
        assert result is False
    
    @patch('os.path.exists')
    def test_environment_setup_import_error(self, mock_exists):
        """Test environment setup with import errors."""
        mock_exists.return_value = True
        
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            scraper = Phase1InstagramScraper()
            result = scraper.test_environment_setup()
        
        assert result is False
    
    def test_show_phase1_summary(self, capsys):
        """Test Phase 1 summary display."""
        scraper = Phase1InstagramScraper()
        scraper.show_phase1_summary()
        
        captured = capsys.readouterr()
        assert "INSTAGRAM PROFILE SCRAPER - PHASE 1 SUMMARY" in captured.out
        assert "Foundation, Login & Backup Accounts" in captured.out
        assert "Virtual environment setup" in captured.out
        assert "ChromeDriver auto-detection" in captured.out
    
    @patch('scraper.InstagramScraper')
    @patch('os.path.exists')
    @patch('utils.detect_chromedriver_path')
    @patch('main.InstagramProfileScraper')
    def test_run_phase1_development_success(self, mock_scraper_class, mock_detect_chrome, mock_exists, mock_instagram_scraper):
        """Test successful Phase 1 development run."""
        mock_exists.return_value = True
        mock_detect_chrome.return_value = "/usr/bin/chromedriver"
        
        # Mock the underlying InstagramScraper
        mock_scraper_obj = Mock()
        mock_scraper_obj.login_with_backup_support.return_value = True
        mock_instagram_scraper.return_value = mock_scraper_obj
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.run_phase1_complete.return_value = True
        mock_scraper_instance.get_session_info.return_value = {
            'session_data': {
                'current_account': 'eprosine009',
                'total_accounts': 2,
                'remaining_accounts': 1
            }
        }
        mock_scraper_instance.__enter__ = Mock(return_value=mock_scraper_instance)
        mock_scraper_instance.__exit__ = Mock(return_value=None)
        mock_scraper_class.return_value = mock_scraper_instance
        
        # Mock the environment setup to return True
        scraper = Phase1InstagramScraper()
        with patch.object(scraper, 'test_environment_setup', return_value=True):
            result = scraper.run_phase1_development()
        
        assert result is True
    
    @patch.object(Phase1InstagramScraper, 'test_environment_setup')
    @patch('main.InstagramProfileScraper')
    def test_run_phase1_development_failure(self, mock_scraper_class, mock_env_test):
        """Test failed Phase 1 development run."""
        mock_env_test.return_value = True
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.run_phase1_complete.return_value = False
        mock_scraper_instance.__enter__ = Mock(return_value=mock_scraper_instance)
        mock_scraper_instance.__exit__ = Mock(return_value=None)
        mock_scraper_class.return_value = mock_scraper_instance
        
        scraper = Phase1InstagramScraper()
        result = scraper.run_phase1_development()
        
        assert result is False


class TestPhase1WorkflowIntegration:
    """Integration tests for complete Phase 1 workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["INSTAGRAM_ACCOUNTS"] = "eprosine009:IniPwBaru123,eprosen2:desember@03"
        os.environ["LOG_TO_FILE"] = "false"
    
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('scraper.InstagramScraper._setup_driver')
    @patch('scraper.InstagramScraper.login_with_backup_support')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_complete_phase1_workflow(self, mock_json_dump, mock_open, mock_login, mock_setup):
        """Test complete Phase 1 workflow from start to finish."""
        mock_login.return_value = True
        
        # Create a mock driver
        mock_driver = Mock()
        mock_driver.current_url = "https://www.instagram.com/"
        mock_driver.get = Mock()
        
        scraper = InstagramProfileScraper()
        
        # Mock the scraper's methods
        with patch.object(scraper, 'scraper') as mock_scraper_obj:
            mock_scraper_obj.driver = mock_driver
            mock_scraper_obj.take_screenshot = Mock()
            
            result = scraper.run_phase1_complete()
        
        assert result is True
        # Verify that results were saved
        assert mock_json_dump.call_count >= 1
    
    @patch('scraper.InstagramScraper')
    @patch('os.path.exists')
    @patch('utils.detect_chromedriver_path')
    @patch('main.InstagramProfileScraper')
    def test_phase1_main_function_success(self, mock_scraper_class, mock_detect_chrome, mock_exists, mock_instagram_scraper):
        """Test Phase 1 main function success path."""
        mock_exists.return_value = True
        mock_detect_chrome.return_value = "/usr/bin/chromedriver"
        
        # Mock the underlying InstagramScraper
        mock_scraper_obj = Mock()
        mock_scraper_obj.login_with_backup_support.return_value = True
        mock_instagram_scraper.return_value = mock_scraper_obj
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.run_phase1_complete.return_value = True
        mock_scraper_instance.get_session_info.return_value = {
            'session_data': {
                'current_account': 'eprosine009',
                'total_accounts': 2,
                'remaining_accounts': 1
            }
        }
        mock_scraper_instance.__enter__ = Mock(return_value=mock_scraper_instance)
        mock_scraper_instance.__exit__ = Mock(return_value=None)
        mock_scraper_class.return_value = mock_scraper_instance
        
        phase1_scraper = Phase1InstagramScraper()
        
        with patch.object(phase1_scraper, 'show_phase1_summary'):
            with patch.object(phase1_scraper, 'test_environment_setup', return_value=True):
                result = phase1_scraper.run_phase1_development()
        
        assert result is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
