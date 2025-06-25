"""
Instagram Profile Scraper - Utilities Module
Phase 1: Foundation, Login & Backup Accounts

This module provides session management and backup account utilities.
"""

import pickle
import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="configuration/.env")

class SessionManager:
    """Manages Instagram session persistence and backup accounts."""
    
    def __init__(self):
        self.session_dir = "configuration"
        self.accounts = self._load_accounts()
        self.current_account_index = 0
        self.logger = logging.getLogger(__name__)
        
    def _load_accounts(self) -> List[Dict[str, str]]:
        """Load Instagram accounts from environment variables."""
        accounts_str = os.getenv("INSTAGRAM_ACCOUNTS", "")
        accounts = []
        
        if accounts_str:
            for account_pair in accounts_str.split(","):
                if ":" in account_pair:
                    username, password = account_pair.strip().split(":", 1)
                    accounts.append({
                        "username": username.strip(),
                        "password": password.strip()
                    })
        
        if not accounts:
            raise ValueError("No Instagram accounts found in environment variables")
            
        return accounts
    
    def get_current_account(self) -> Dict[str, str]:
        """Get the current active account."""
        if self.current_account_index >= len(self.accounts):
            raise IndexError("No more backup accounts available")
        
        return self.accounts[self.current_account_index]
    
    def switch_to_backup_account(self) -> Optional[Dict[str, str]]:
        """Switch to the next backup account."""
        self.current_account_index += 1
        
        if self.current_account_index >= len(self.accounts):
            self.logger.error("All backup accounts exhausted")
            return None
            
        backup_account = self.get_current_account()
        self.logger.info(f"Switching to backup account: {backup_account['username']}")
        return backup_account
    
    def save_session(self, driver, account_username: str):
        """Save session cookies for the specified account."""
        try:
            session_file = os.path.join(self.session_dir, f"session_{account_username}.pkl")
            cookies = driver.get_cookies()
            
            with open(session_file, 'wb') as file:
                pickle.dump(cookies, file)
                
            self.logger.info(f"Session saved for account: {account_username}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session for {account_username}: {str(e)}")
    
    def load_session(self, driver, account_username: str) -> bool:
        """Load session cookies for the specified account."""
        try:
            session_file = os.path.join(self.session_dir, f"session_{account_username}.pkl")
            
            if not os.path.exists(session_file):
                self.logger.info(f"No existing session found for {account_username}")
                return False
            
            with open(session_file, 'rb') as file:
                cookies = pickle.load(file)
            
            # Navigate to Instagram first to set cookies
            driver.get("https://www.instagram.com/")
            time.sleep(2)
            
            # Add cookies to the driver
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.warning(f"Failed to add cookie: {str(e)}")
            
            # Refresh to apply cookies
            driver.refresh()
            time.sleep(3)
            
            self.logger.info(f"Session loaded for account: {account_username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load session for {account_username}: {str(e)}")
            return False
    
    def clear_session(self, account_username: str):
        """Clear session file for the specified account."""
        try:
            session_file = os.path.join(self.session_dir, f"session_{account_username}.pkl")
            
            if os.path.exists(session_file):
                os.remove(session_file)
                self.logger.info(f"Session cleared for account: {account_username}")
            
        except Exception as e:
            self.logger.error(f"Failed to clear session for {account_username}: {str(e)}")
    
    def get_account_count(self) -> int:
        """Get total number of available accounts."""
        return len(self.accounts)
    
    def get_remaining_accounts(self) -> int:
        """Get number of remaining backup accounts."""
        return len(self.accounts) - self.current_account_index - 1
    
    def reset_account_index(self):
        """Reset to the first account."""
        self.current_account_index = 0


class RateLimiter:
    """Implements rate limiting to avoid Instagram bans."""
    
    def __init__(self):
        self.request_delay = float(os.getenv("REQUEST_DELAY", "2"))
        self.login_delay = float(os.getenv("LOGIN_DELAY", "5"))
        self.last_request_time = 0
        self.last_login_time = 0
    
    def wait_for_request(self):
        """Wait before making a request to avoid rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def wait_for_login(self):
        """Wait before login attempt to avoid rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_login_time
        
        if time_since_last < self.login_delay:
            sleep_time = self.login_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_login_time = time.time()


def setup_logging() -> logging.Logger:
    """Set up logging configuration for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )
    
    logger = logging.getLogger("ig_scraper")
    
    if log_to_file:
        # Add file handler
        file_handler = logging.FileHandler(
            f"logs/detailed_{int(time.time())}.log"
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        
        # Add error file handler
        error_handler = logging.FileHandler(
            f"logs/errors_{int(time.time())}.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(error_handler)
    
    return logger


def detect_chromedriver_path() -> str:
    """Detect ChromeDriver path automatically."""
    # Check environment variable first
    env_path = os.getenv("CHROMEDRIVER_PATH", "")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Common paths for ChromeDriver
    common_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/opt/google/chrome/chromedriver",
        "/snap/bin/chromium.chromedriver",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Check if chromedriver is in PATH
    import shutil
    which_result = shutil.which("chromedriver")
    if which_result:
        return which_result
    
    raise FileNotFoundError(
        "ChromeDriver not found. Please install it or set CHROMEDRIVER_PATH in .env file"
    )
