#!/usr/bin/env python3
"""
Instagram Profile Scraper - Phase 1 Main File
Phase 1: Foundation, Login & Backup Accounts

This is the main entry point for Phase 1 development and testing.
"""

import sys
import os
import time

# Add core files directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper
from utils import setup_logging


class Phase1InstagramScraper:
    """Phase 1 specific implementation of Instagram scraper."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scraper = None
        
    def run_phase1_development(self):
        """Run Phase 1 development workflow."""
        try:
            self.logger.info("=== Phase 1 Development Execution ===")
            self.logger.info("Features to implement:")
            self.logger.info("- Virtual environment and dependencies")
            self.logger.info("- ChromeDriver configuration")
            self.logger.info("- Selenium-based Instagram login")
            self.logger.info("- Session persistence with cookies")
            self.logger.info("- Multiple backup account support")
            self.logger.info("- Basic error handling")
            
            # Initialize the main scraper
            with InstagramProfileScraper() as scraper:
                self.scraper = scraper
                
                # Run Phase 1 complete workflow
                success = scraper.run_phase1_complete()
                
                if success:
                    self.logger.info("=== Phase 1 Development Completed Successfully ===")
                    
                    # Display session information
                    session_info = scraper.get_session_info()
                    self.logger.info("Session Information:")
                    self.logger.info(f"- Current Account: {session_info['session_data'].get('current_account', 'N/A')}")
                    self.logger.info(f"- Total Accounts: {session_info['session_data'].get('total_accounts', 0)}")
                    self.logger.info(f"- Remaining Backups: {session_info['session_data'].get('remaining_accounts', 0)}")
                    
                    # Ready for next phase
                    self.logger.info("Ready to proceed to Phase 2: Profile Extraction")
                    return True
                else:
                    self.logger.error("Phase 1 development failed")
                    return False
                    
        except KeyboardInterrupt:
            self.logger.info("Phase 1 execution interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Critical error in Phase 1 development: {str(e)}")
            return False
    
    def test_environment_setup(self):
        """Test if the environment is properly set up for Phase 1."""
        try:
            self.logger.info("=== Testing Environment Setup ===")
            
            # Check if .env file exists
            env_file = os.path.join("configuration", ".env")
            if os.path.exists(env_file):
                self.logger.info("✓ Environment configuration file found")
            else:
                self.logger.error("✗ Environment configuration file not found")
                return False
            
            # Check if requirements.txt exists
            req_file = os.path.join("configuration", "requirements.txt")
            if os.path.exists(req_file):
                self.logger.info("✓ Requirements file found")
            else:
                self.logger.error("✗ Requirements file not found")
                return False
            
            # Test imports
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                self.logger.info("✓ Selenium imports successful")
            except ImportError as e:
                self.logger.error(f"✗ Selenium import failed: {str(e)}")
                return False
            
            try:
                from dotenv import load_dotenv
                self.logger.info("✓ Python-dotenv import successful")
            except ImportError as e:
                self.logger.error(f"✗ Python-dotenv import failed: {str(e)}")
                return False
            
            # Test ChromeDriver detection
            try:
                from utils import detect_chromedriver_path
                chromedriver_path = detect_chromedriver_path()
                self.logger.info(f"✓ ChromeDriver found at: {chromedriver_path}")
            except Exception as e:
                self.logger.warning(f"⚠ ChromeDriver detection issue: {str(e)}")
                self.logger.warning("You may need to install ChromeDriver manually")
            
            self.logger.info("=== Environment Setup Test Completed ===")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during environment setup test: {str(e)}")
            return False
    
    def show_phase1_summary(self):
        """Display Phase 1 implementation summary."""
        print("\n" + "="*60)
        print("📸 INSTAGRAM PROFILE SCRAPER - PHASE 1 SUMMARY")
        print("="*60)
        print("Phase 1: Foundation, Login & Backup Accounts")
        print("\n🚀 Implemented Features:")
        print("- ✓ Virtual environment setup with dependencies")
        print("- ✓ ChromeDriver auto-detection and configuration")
        print("- ✓ Selenium WebDriver initialization")
        print("- ✓ Instagram login automation")
        print("- ✓ Session persistence with cookie storage")
        print("- ✓ Multiple backup account support")
        print("- ✓ Rate limiting to avoid Instagram bans")
        print("- ✓ Comprehensive error handling")
        print("- ✓ Enhanced logging system")
        
        print("\n📁 Files Created:")
        print("- core files/utils.py - Session and backup account utilities")
        print("- core files/scraper.py - Core scraper logic with login")
        print("- core files/main.py - Main entry point")
        print("- phase files/phase1_scraper.py - Phase 1 main file")
        print("- configuration/requirements.txt - Dependencies")
        print("- configuration/.env - Environment configuration")
        
        print("\n🔧 Environment:")
        print("- Python 3.8+ with virtual environment")
        print("- Selenium WebDriver 4.15.2")
        print("- ChromeDriver (auto-detected)")
        print("- Instagram dummy accounts configured")
        
        print("\n📝 Next Steps:")
        print("- Phase 2: Profile Extraction")
        print("- Phase 3: Post Scraping")
        print("- Phase 4: Advanced Parsing & Cleaning")
        print("="*60)


def main():
    """Main function for Phase 1 execution."""
    print("Instagram Profile Scraper - Phase 1")
    print("Foundation, Login & Backup Accounts")
    print("-" * 50)
    
    phase1_scraper = Phase1InstagramScraper()
    
    # Test environment setup first
    if not phase1_scraper.test_environment_setup():
        print("\n❌ Environment setup test failed!")
        print("Please ensure all dependencies are installed:")
        print("1. Run: python -m venv venv")
        print("2. Run: source venv/bin/activate")
        print("3. Run: pip install -r configuration/requirements.txt")
        print("4. Install ChromeDriver if needed")
        return False
    
    print("\n✅ Environment setup test passed!")
    
    # Run Phase 1 development
    success = phase1_scraper.run_phase1_development()
    
    if success:
        phase1_scraper.show_phase1_summary()
        print("\n🎉 Phase 1 completed successfully!")
        print("You can now proceed to Phase 2: Profile Extraction")
        return True
    else:
        print("\n❌ Phase 1 failed!")
        print("Please check the logs in the 'logs/' directory for detailed error information.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
        sys.exit(1)
