"""
Instagram Profile Scraper - Output Logger Module
Phase 5: Enhanced Logging System

This module provides enhanced logging capabilities with session tracking
and detailed operation logging for search functionality.
"""

import logging
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class OutputLogger:
    """Enhanced logging system for Instagram scraper operations."""
    
    def __init__(self, base_log_dir: str = "logs"):
        self.base_log_dir = base_log_dir
        self.session_id = int(time.time())
        self.setup_directories()
        self.setup_loggers()
        
    def setup_directories(self):
        """Create necessary logging directories."""
        os.makedirs(self.base_log_dir, exist_ok=True)
        
    def setup_loggers(self):
        """Set up different loggers for different types of operations."""
        
        # Main detailed logger
        self.detailed_logger = logging.getLogger(f'detailed_{self.session_id}')
        self.detailed_logger.setLevel(logging.DEBUG)
        
        detailed_handler = logging.FileHandler(
            os.path.join(self.base_log_dir, f'detailed_{self.session_id}.log')
        )
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        detailed_handler.setFormatter(detailed_formatter)
        self.detailed_logger.addHandler(detailed_handler)
        
        # Error logger
        self.error_logger = logging.getLogger(f'errors_{self.session_id}')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(
            os.path.join(self.base_log_dir, f'errors_{self.session_id}.log')
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s - %(pathname)s:%(lineno)d'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Search operations logger
        self.search_logger = logging.getLogger(f'search_{self.session_id}')
        self.search_logger.setLevel(logging.INFO)
        
        search_handler = logging.FileHandler(
            os.path.join(self.base_log_dir, f'search_{self.session_id}.log')
        )
        search_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        search_handler.setFormatter(search_formatter)
        self.search_logger.addHandler(search_handler)
        
        # Performance logger
        self.performance_logger = logging.getLogger(f'performance_{self.session_id}')
        self.performance_logger.setLevel(logging.INFO)
        
        perf_handler = logging.FileHandler(
            os.path.join(self.base_log_dir, f'performance_{self.session_id}.log')
        )
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        self.performance_logger.addHandler(perf_handler)
        
    def log_session_start(self, search_type: str, search_target: str, parameters: Dict):
        """Log the start of a scraping session."""
        session_info = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'search_type': search_type,
            'search_target': search_target,
            'parameters': parameters
        }
        
        self.detailed_logger.info(f"=== SESSION START ===")
        self.detailed_logger.info(f"Session ID: {self.session_id}")
        self.detailed_logger.info(f"Search Type: {search_type}")
        self.detailed_logger.info(f"Search Target: {search_target}")
        self.detailed_logger.info(f"Parameters: {json.dumps(parameters, indent=2)}")
        
        self.search_logger.info(f"Session {self.session_id} started - {search_type} search for '{search_target}'")
        
        return session_info
        
    def log_session_end(self, session_info: Dict, results_count: int, success: bool):
        """Log the end of a scraping session."""
        end_time = datetime.now().isoformat()
        duration = time.time() - self.session_id
        
        self.detailed_logger.info(f"=== SESSION END ===")
        self.detailed_logger.info(f"Session ID: {self.session_id}")
        self.detailed_logger.info(f"End Time: {end_time}")
        self.detailed_logger.info(f"Duration: {duration:.2f} seconds")
        self.detailed_logger.info(f"Results Count: {results_count}")
        self.detailed_logger.info(f"Success: {success}")
        
        self.search_logger.info(
            f"Session {self.session_id} ended - Success: {success}, "
            f"Results: {results_count}, Duration: {duration:.2f}s"
        )
        
        session_info.update({
            'end_time': end_time,
            'duration_seconds': duration,
            'results_count': results_count,
            'success': success
        })
        
        return session_info
        
    def log_search_operation(self, operation: str, details: Dict):
        """Log a specific search operation."""
        self.detailed_logger.info(f"Search Operation: {operation}")
        self.detailed_logger.info(f"Details: {json.dumps(details, indent=2)}")
        
        self.search_logger.info(f"{operation}: {details.get('summary', 'No summary')}")
        
    def log_post_extraction(self, post_url: str, extraction_result: Dict):
        """Log post extraction details."""
        self.detailed_logger.info(f"Post Extraction: {post_url}")
        self.detailed_logger.debug(f"Extraction Result: {json.dumps(extraction_result, indent=2)}")
        
        success = extraction_result.get('success', False)
        self.search_logger.info(f"Post extracted: {post_url} - Success: {success}")
        
    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Log an error with context."""
        error_details = {
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'context': context or {}
        }
        
        self.error_logger.error(f"{error_type}: {error_message}")
        if context:
            self.error_logger.error(f"Context: {json.dumps(context, indent=2)}")
            
        self.detailed_logger.error(f"ERROR - {error_type}: {error_message}")
        
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log a performance metric."""
        self.performance_logger.info(f"{metric_name}: {value} {unit}")
        self.detailed_logger.debug(f"Performance - {metric_name}: {value} {unit}")
        
    def log_rate_limit_info(self, action: str, delay: float):
        """Log rate limiting information."""
        self.detailed_logger.info(f"Rate Limit - {action}: Waiting {delay} seconds")
        self.performance_logger.info(f"Rate Limit Delay: {delay}s for {action}")
        
    def log_search_algorithm_step(self, algorithm_type: str, step: str, result: Any):
        """Log specific algorithm steps for debugging."""
        self.detailed_logger.debug(f"Algorithm [{algorithm_type}] - Step: {step}")
        self.detailed_logger.debug(f"Algorithm [{algorithm_type}] - Result: {str(result)[:200]}...")
        
    def log_data_quality_assessment(self, post_url: str, quality_score: float, quality_details: Dict):
        """Log data quality assessment."""
        self.detailed_logger.info(f"Data Quality Assessment: {post_url}")
        self.detailed_logger.info(f"Quality Score: {quality_score}")
        self.detailed_logger.debug(f"Quality Details: {json.dumps(quality_details, indent=2)}")
        
    def create_session_summary(self, session_info: Dict, posts_data: List[Dict]) -> Dict:
        """Create a comprehensive session summary."""
        summary = {
            'session_metadata': session_info,
            'statistics': {
                'total_posts_found': len(posts_data),
                'successful_extractions': sum(1 for post in posts_data if post.get('success', False)),
                'failed_extractions': sum(1 for post in posts_data if not post.get('success', False)),
                'average_quality_score': 0.0
            },
            'posts_summary': []
        }
        
        # Calculate average quality score
        quality_scores = [post.get('quality_score', 0) for post in posts_data if 'quality_score' in post]
        if quality_scores:
            summary['statistics']['average_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        # Create posts summary
        for post in posts_data:
            post_summary = {
                'url': post.get('url', 'Unknown'),
                'success': post.get('success', False),
                'quality_score': post.get('quality_score', 0),
                'extraction_time': post.get('extraction_time', 'Unknown')
            }
            summary['posts_summary'].append(post_summary)
        
        # Log the summary
        self.detailed_logger.info("=== SESSION SUMMARY ===")
        self.detailed_logger.info(f"Session Summary: {json.dumps(summary, indent=2)}")
        
        return summary
        
    def get_session_id(self) -> int:
        """Get the current session ID."""
        return self.session_id
        
    def get_log_files(self) -> Dict[str, str]:
        """Get paths to all log files for this session."""
        return {
            'detailed': os.path.join(self.base_log_dir, f'detailed_{self.session_id}.log'),
            'errors': os.path.join(self.base_log_dir, f'errors_{self.session_id}.log'),
            'search': os.path.join(self.base_log_dir, f'search_{self.session_id}.log'),
            'performance': os.path.join(self.base_log_dir, f'performance_{self.session_id}.log')
        }
        
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Clean up old log files."""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            for filename in os.listdir(self.base_log_dir):
                file_path = os.path.join(self.base_log_dir, filename)
                if os.path.isfile(file_path):
                    file_mod_time = os.path.getmtime(file_path)
                    if file_mod_time < cutoff_time:
                        os.remove(file_path)
                        self.detailed_logger.info(f"Cleaned up old log file: {filename}")
                        
        except Exception as e:
            self.log_error("LogCleanup", f"Error cleaning up old logs: {str(e)}")
