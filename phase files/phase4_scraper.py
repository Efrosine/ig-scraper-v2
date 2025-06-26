#!/usr/bin/env python3
"""
Phase 4 Instagram Profile Scraper
Advanced Parsing & Cleaning

This module runs the Phase 4 implementation with:
- Enhanced BeautifulSoup parsing
- Data cleaning and normalization
- Quality scoring for posts
- Metadata extraction from captions (hashtags, mentions, etc.)
- Text normalization and emoji handling
"""

import sys
import os
import json
import time
from typing import Dict, Any

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper
from utils import setup_logging


class Phase4InstagramScraper:
    """Phase 4 Instagram Scraper with advanced parsing and cleaning."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scraper = None
        
    def run_phase4(self, username: str = "malangraya_info", post_count: int = 5, 
                   comment_count: int = 5, min_quality: float = 0.0) -> Dict[str, Any]:
        """
        Run Phase 4: Advanced Parsing & Cleaning
        
        Args:
            username: Instagram username to scrape
            post_count: Number of posts to extract
            comment_count: Number of comments per post
            min_quality: Minimum quality score (0.0-1.0)
            
        Returns:
            Dictionary containing the results
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("🚀 Phase 4: Advanced Parsing & Cleaning")
            self.logger.info("=" * 60)
            self.logger.info(f"Target Username: @{username}")
            self.logger.info(f"Posts to extract: {post_count}")
            self.logger.info(f"Comments per post: {comment_count}")
            self.logger.info(f"Minimum quality score: {min_quality}")
            self.logger.info("=" * 60)
            
            # Initialize the scraper
            with InstagramProfileScraper() as scraper:
                self.scraper = scraper
                
                # Step 1: Initialize scraper
                self.logger.info("Step 1: Initializing scraper with Phase 4 enhancements...")
                if not scraper.initialize():
                    raise Exception("Failed to initialize scraper")
                
                self.logger.info("✅ Scraper initialized successfully")
                
                # Step 2: Test basic navigation
                self.logger.info("Step 2: Testing basic navigation...")
                if not scraper.test_basic_navigation():
                    self.logger.warning("⚠️ Navigation test failed, but continuing...")
                else:
                    self.logger.info("✅ Navigation test successful")
                
                # Step 3: Enhanced post scraping with cleaning
                self.logger.info(f"Step 3: Enhanced post scraping for @{username}...")
                results = scraper.scrape_posts_enhanced(
                    username=username,
                    post_count=post_count,
                    comment_count=comment_count,
                    min_quality=min_quality
                )
                
                if "error" in results:
                    self.logger.error(f"❌ Post scraping failed: {results['error']}")
                    return results
                
                posts_found = len(results.get("results", []))
                avg_quality = results.get("cleaning_stats", {}).get("avg_quality_score", 0.0)
                
                self.logger.info(f"✅ Enhanced post scraping completed")
                self.logger.info(f"   Posts extracted: {posts_found}")
                self.logger.info(f"   Average quality score: {avg_quality:.2f}")
                
                # Step 4: Save results
                self.logger.info("Step 4: Saving Phase 4 results...")
                output_file = scraper.save_phase4_results(results, username)
                
                if output_file:
                    self.logger.info(f"✅ Results saved to: {output_file}")
                else:
                    self.logger.warning("⚠️ Failed to save results to file")
                
                # Step 5: Display summary
                self.logger.info("=" * 60)
                self.logger.info("📊 Phase 4 Summary")
                self.logger.info("=" * 60)
                
                session_info = scraper.get_session_info()
                cleaning_stats = results.get("cleaning_stats", {})
                
                self.logger.info(f"Current Account: {session_info['session_data'].get('current_account', 'Unknown')}")
                self.logger.info(f"Target Username: @{username}")
                self.logger.info(f"Posts Requested: {post_count}")
                self.logger.info(f"Posts Extracted: {results.get('total_posts_extracted', 0)}")
                self.logger.info(f"Posts After Cleaning: {results.get('posts_after_cleaning', 0)}")
                self.logger.info(f"Average Quality Score: {cleaning_stats.get('avg_quality_score', 0.0):.2f}")
                self.logger.info(f"High Quality Posts: {cleaning_stats.get('high_quality_count', 0)}")
                self.logger.info(f"Features Applied: {', '.join(results.get('features_applied', []))}")
                
                # Sample post quality data
                sample_posts = results.get("results", [])[:3]  # Show first 3
                if sample_posts:
                    self.logger.info("\n📝 Sample Posts Quality Analysis:")
                    for i, post in enumerate(sample_posts, 1):
                        quality = post.get("quality_score", 0.0)
                        caption_len = len(post.get("caption", ""))
                        comments_count = len(post.get("comments", {}))
                        metadata = post.get("metadata", {})
                        hashtags_count = len(metadata.get("hashtags", []))
                        mentions_count = len(metadata.get("mentions", []))
                        
                        self.logger.info(f"   Post {i}: Quality={quality:.2f}, Caption={caption_len} chars, "
                                       f"Comments={comments_count}, Hashtags={hashtags_count}, Mentions={mentions_count}")
                
                self.logger.info("=" * 60)
                self.logger.info("🎉 Phase 4 completed successfully!")
                self.logger.info("=" * 60)
                
                return results
                
        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Phase 4 interrupted by user")
            return {"error": "User interruption", "phase": 4}
            
        except Exception as e:
            self.logger.error(f"❌ Phase 4 failed: {str(e)}")
            return {"error": str(e), "phase": 4}
    
    def demonstrate_features(self, username: str = "malangraya_info") -> Dict[str, Any]:
        """
        Demonstrate Phase 4 features with detailed analysis.
        
        Args:
            username: Username to analyze
            
        Returns:
            Detailed analysis results
        """
        try:
            self.logger.info("🔍 Phase 4 Feature Demonstration")
            self.logger.info("=" * 50)
            
            # Run with different quality thresholds to show filtering
            results_low = self.run_phase4(username, post_count=3, comment_count=3, min_quality=0.0)
            results_high = self.run_phase4(username, post_count=3, comment_count=3, min_quality=0.7)
            
            if "error" not in results_low and "error" not in results_high:
                low_count = len(results_low.get("results", []))
                high_count = len(results_high.get("results", []))
                
                self.logger.info(f"📈 Quality Filtering Demonstration:")
                self.logger.info(f"   No quality filter: {low_count} posts")
                self.logger.info(f"   High quality (>0.7): {high_count} posts")
                self.logger.info(f"   Quality filtering effectiveness: {((low_count - high_count) / low_count * 100):.1f}% filtered")
            
            return {
                "low_quality_results": results_low,
                "high_quality_results": results_high,
                "demonstration_complete": True
            }
            
        except Exception as e:
            self.logger.error(f"Feature demonstration failed: {str(e)}")
            return {"error": str(e)}


def main():
    """Main execution function."""
    try:
        # Configuration
        USERNAME = "malangraya_info"  # Target Instagram username
        POST_COUNT = 5  # Number of posts to extract
        COMMENT_COUNT = 5  # Comments per post
        MIN_QUALITY = 0.0  # Minimum quality score (0.0 = no filtering)
        
        print("🚀 Starting Phase 4: Advanced Parsing & Cleaning")
        print(f"Target: @{USERNAME}")
        
        # Run Phase 4
        phase4_scraper = Phase4InstagramScraper()
        results = phase4_scraper.run_phase4(
            username=USERNAME,
            post_count=POST_COUNT,
            comment_count=COMMENT_COUNT,
            min_quality=MIN_QUALITY
        )
        
        if "error" in results:
            print(f"❌ Phase 4 failed: {results['error']}")
            return 1
        
        print("\n🎉 Phase 4 completed successfully!")
        print(f"📁 Check the 'output/' directory for detailed results")
        
        # Optional: Run feature demonstration
        demo_input = input("\n🔍 Run feature demonstration? (y/N): ").strip().lower()
        if demo_input == 'y':
            print("\n🔍 Running feature demonstration...")
            demo_results = phase4_scraper.demonstrate_features(USERNAME)
            if "error" not in demo_results:
                print("✅ Feature demonstration completed!")
            else:
                print(f"❌ Feature demonstration failed: {demo_results['error']}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Phase 4 interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Critical error in Phase 4: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
