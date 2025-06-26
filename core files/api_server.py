"""
Instagram Profile Scraper - API Server Module
Phase 7: HTTP Endpoint Implementation

This module provides a Flask-based HTTP endpoint for triggering scraping operations.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from datetime import datetime

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from main import InstagramProfileScraper
from utils import setup_logging, load_environment_variables


class InstagramScrapingAPI:
    """Flask API server for Instagram scraping operations."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.logger = setup_logging()
        self.env_vars = load_environment_variables()
        self._setup_routes()
        
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "Instagram Profile Scraper API"
            })
        
        @self.app.route('/scrape', methods=['POST'])
        def scrape_posts():
            """Main scraping endpoint."""
            try:
                return self._handle_scrape_request()
            except Exception as e:
                self.logger.error(f"Scrape request failed: {str(e)}")
                return jsonify({
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
    
    def _handle_scrape_request(self) -> tuple:
        """Handle the scraping request with validation."""
        
        # Parse request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be valid JSON"
            }), 400
        
        # Validate and extract parameters
        validation_result = self._validate_request(request_data)
        if validation_result['error']:
            return jsonify(validation_result), 400
        
        # Extract validated parameters
        accounts = validation_result['accounts']
        suspected_account = validation_result['suspected_account']
        post_count = validation_result['post_count']
        comment_count = validation_result['comment_count']
        
        self.logger.info(f"Processing scrape request: suspected_account={suspected_account}, "
                        f"post_count={post_count}, comment_count={comment_count}")
        
        # Perform scraping
        try:
            # Prepare custom accounts if provided
            custom_accounts = None
            if accounts:
                custom_accounts = [
                    {"username": acc["username"], "password": acc["password"]}
                    for acc in accounts
                ]
            
            # Create scraper with custom accounts
            scraper = InstagramProfileScraper(custom_accounts=custom_accounts)
            
            # Initialize scraper
            if not scraper.initialize():
                return jsonify({
                    "error": "Scraping failed",
                    "message": "Failed to initialize scraper or login"
                }), 500
            
            # Navigate to suspected account profile
            profile_data = scraper.scrape_profile(suspected_account)
            if not profile_data:
                return jsonify({
                    "error": "Scraping failed",
                    "message": f"Failed to access profile: {suspected_account}"
                }), 500
            
            # Extract posts
            posts_data = scraper.scrape_posts(post_count, comment_count)
            
            # Cleanup
            scraper.cleanup()
            
            # Format response
            response_data = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "suspected_account": suspected_account,
                    "post_count": post_count,
                    "comment_count": comment_count,
                    "accounts_used": len(accounts) if accounts else "default"
                },
                "results": posts_data,
                "metadata": {
                    "total_posts_extracted": len(posts_data),
                    "profile_info": profile_data
                }
            }
            
            # Save results
            self._save_results(response_data)
            
            self.logger.info(f"Scraping completed successfully: {len(posts_data)} posts extracted")
            return jsonify(response_data), 200
            
        except Exception as e:
            self.logger.error(f"Scraping operation failed: {str(e)}")
            return jsonify({
                "error": "Scraping failed",
                "message": str(e)
            }), 500
    
    def _validate_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the scraping request parameters."""
        
        result = {
            "error": False,
            "message": "",
            "accounts": None,
            "suspected_account": None,
            "post_count": None,
            "comment_count": None
        }
        
        try:
            # Validate accounts (optional)
            accounts = data.get('accounts', [])
            if accounts:
                if not isinstance(accounts, list):
                    result['error'] = True
                    result['message'] = "Accounts must be a list"
                    return result
                
                for acc in accounts:
                    if not isinstance(acc, dict) or 'username' not in acc or 'password' not in acc:
                        result['error'] = True
                        result['message'] = "Each account must have 'username' and 'password' fields"
                        return result
                
                result['accounts'] = accounts
            
            # Validate suspected_account (required)
            suspected_account = data.get('suspected_account')
            if not suspected_account:
                # Use default if not provided
                suspected_account = self.env_vars.get('DEFAULT_SUSPECTED_ACCOUNT', 'malangraya_info')
            
            if not isinstance(suspected_account, str) or not suspected_account.strip():
                result['error'] = True
                result['message'] = "suspected_account must be a non-empty string"
                return result
            
            result['suspected_account'] = suspected_account.strip()
            
            # Validate post_count (optional, use default if not provided)
            post_count = data.get('post_count')
            if post_count is None:
                post_count = int(self.env_vars.get('DEFAULT_POST_COUNT', 10))
            
            if not isinstance(post_count, int) or post_count < 0:
                result['error'] = True
                result['message'] = "post_count must be a non-negative integer"
                return result
            
            result['post_count'] = post_count
            
            # Validate comment_count (optional, use default if not provided)
            comment_count = data.get('comment_count')
            if comment_count is None:
                comment_count = int(self.env_vars.get('DEFAULT_COMMENT_COUNT', 5))
            
            if not isinstance(comment_count, int) or comment_count < 0:
                result['error'] = True
                result['message'] = "comment_count must be a non-negative integer"
                return result
            
            result['comment_count'] = comment_count
            
            return result
            
        except Exception as e:
            result['error'] = True
            result['message'] = f"Validation error: {str(e)}"
            return result
    
    def _save_results(self, data: Dict[str, Any]):
        """Save scraping results to output directory."""
        try:
            # Ensure output directory exists
            output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save main result
            result_file = os.path.join(output_dir, "result.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(output_dir, f"backup_{timestamp}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {result_file} and {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def run(self, host='0.0.0.0', port=None, debug=False):
        """Run the Flask application."""
        if port is None:
            port = int(self.env_vars.get('FORWARDING_PORT', 5000))
        
        self.logger.info(f"Starting Instagram Scraping API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory function to create Flask app instance."""
    api = InstagramScrapingAPI()
    return api.app


if __name__ == "__main__":
    api = InstagramScrapingAPI()
    api.run(debug=True)
