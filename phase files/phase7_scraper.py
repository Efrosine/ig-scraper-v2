"""
Instagram Profile Scraper - Phase 7 Main Script
Phase 7: HTTP Endpoint Implementation

This script serves as the main entry point for Phase 7, running the HTTP endpoint
for triggering Instagram scraping operations via API calls.
"""

import os
import sys
import signal
import logging
from typing import Optional

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from api_server import InstagramScrapingAPI
from utils import setup_logging, load_environment_variables


class Phase7InstagramScraper:
    """Phase 7 main class for running HTTP endpoint."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.env_vars = load_environment_variables()
        self.api_server = None
        
    def run(self):
        """Run Phase 7 HTTP endpoint server."""
        try:
            self.logger.info("=== Instagram Profile Scraper - Phase 7 ===")
            self.logger.info("HTTP Endpoint Implementation")
            self.logger.info("Starting Flask API server...")
            
            # Create API server
            self.api_server = InstagramScrapingAPI()
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Get server configuration
            host = self.env_vars.get('API_HOST', '0.0.0.0')
            port = int(self.env_vars.get('FORWARDING_PORT', 5000))
            debug = self.env_vars.get('DEBUG', 'false').lower() == 'true'
            
            self.logger.info(f"Server configuration:")
            self.logger.info(f"- Host: {host}")
            self.logger.info(f"- Port: {port}")
            self.logger.info(f"- Debug: {debug}")
            self.logger.info("Available endpoints:")
            self.logger.info("- GET  /health - Health check")
            self.logger.info("- POST /scrape - Scraping endpoint")
            self.logger.info("")
            self.logger.info("Example API usage:")
            self.logger.info(f"curl -X POST http://localhost:{port}/scrape \\")
            self.logger.info("  -H 'Content-Type: application/json' \\")
            self.logger.info("  -d '{")
            self.logger.info('    "accounts": [{"username": "user1", "password": "pass1"}],')
            self.logger.info('    "suspected_account": "malangraya_info",')
            self.logger.info('    "post_count": 10,')
            self.logger.info('    "comment_count": 5')
            self.logger.info("  }'")
            self.logger.info("")
            
            # Start server
            self.api_server.run(host=host, port=port, debug=debug)
            
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Error running Phase 7: {str(e)}")
            raise
        finally:
            self._cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            self.logger.info("Cleaning up resources...")
            # Add any cleanup logic here
            self.logger.info("Phase 7 cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def test_api(self):
        """Test the API functionality."""
        try:
            self.logger.info("Testing API functionality...")
            
            # Import requests for testing
            import requests
            import time
            
            # Start server in background (this would need threading for real testing)
            self.logger.info("For testing, please run the server in another terminal:")
            self.logger.info("python phase7_scraper.py")
            self.logger.info("")
            self.logger.info("Then test with:")
            port = int(self.env_vars.get('FORWARDING_PORT', 5000))
            self.logger.info(f"curl -X GET http://localhost:{port}/health")
            
        except Exception as e:
            self.logger.error(f"API test error: {str(e)}")


def main():
    """Main function to run Phase 7."""
    try:
        scraper = Phase7InstagramScraper()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "test":
                scraper.test_api()
                return
            elif sys.argv[1] == "help":
                print("Phase 7 Instagram Scraper - HTTP Endpoint")
                print("Usage:")
                print("  python phase7_scraper.py          - Run the API server")
                print("  python phase7_scraper.py test     - Show testing instructions")
                print("  python phase7_scraper.py help     - Show this help message")
                return
        
        # Run the server
        scraper.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Phase 7 failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
