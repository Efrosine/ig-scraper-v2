"""
Instagram Profile Scraper - Phase 2
Phase 2: Profile Extraction

This module serves as the main file to run Phase 2 profile extraction functionality.
"""

import sys
import os
import time

# Add the core files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from main import InstagramProfileScraper


class Phase2InstagramScraper:
    """Phase 2 Instagram Profile Scraper for profile extraction."""
    
    def __init__(self):
        self.main_scraper = None
        
    def initialize(self) -> bool:
        """Initialize the main scraper for Phase 2."""
        try:
            print("=== Phase 2: Profile Extraction ===")
            print("Initializing scraper...")
            
            self.main_scraper = InstagramProfileScraper()
            
            # Initialize Phase 1 foundation first
            if not self.main_scraper.initialize():
                print("❌ Failed to initialize Phase 1 foundation")
                return False
            
            print("✅ Phase 1 foundation initialized successfully")
            print("✅ Ready for Phase 2 profile extraction")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Phase 2: {str(e)}")
            return False
    
    def extract_profile(self, username: str = "malangraya_info") -> bool:
        """
        Extract profile data for the specified username.
        
        Args:
            username (str): Instagram username to extract (default: malangraya_info)
            
        Returns:
            bool: Success status
        """
        try:
            if not self.main_scraper:
                print("❌ Scraper not initialized")
                return False
            
            print(f"\n🔍 Starting profile extraction for @{username}")
            
            # Extract profile data
            results = self.main_scraper.extract_profile(username)
            
            if results.get("success", False):
                print(f"✅ Profile extraction successful for @{username}")
                
                # Save results
                output_file = self.main_scraper.save_phase2_results(results, username)
                if output_file:
                    print(f"📁 Results saved to: {output_file}")
                else:
                    print("⚠️ Failed to save results")
                
                # Display summary
                profile_data = results.get("profile_data", {})
                print(f"\n📊 Profile Summary:")
                print(f"   Username: @{profile_data.get('username', 'N/A')}")
                print(f"   Display Name: {profile_data.get('display_name', 'N/A')}")
                print(f"   Posts Count: {profile_data.get('posts_count', 'N/A')}")
                print(f"   Followers: {profile_data.get('followers_count', 'N/A')}")
                print(f"   Following: {profile_data.get('following_count', 'N/A')}")
                print(f"   Bio: {profile_data.get('bio', 'N/A')[:100]}...")
                
                return True
            else:
                error = results.get("error", "Unknown error")
                print(f"❌ Profile extraction failed: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Error during profile extraction: {str(e)}")
            return False
    
    def run_phase2_demo(self) -> bool:
        """Run Phase 2 demonstration with default profile."""
        try:
            print("\n=== Phase 2 Demonstration ===")
            print("This will extract profile data from @malangraya_info")
            
            # Extract default profile
            success = self.extract_profile("malangraya_info")
            
            if success:
                print("\n✅ Phase 2 demonstration completed successfully!")
                print("📋 Next steps:")
                print("   - Phase 3: Post Scraping")
                print("   - Phase 4: Advanced Parsing & Cleaning")
                return True
            else:
                print("\n❌ Phase 2 demonstration failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during Phase 2 demonstration: {str(e)}")
            return False
    
    def run_phase2_custom(self, username: str) -> bool:
        """
        Run Phase 2 with custom username.
        
        Args:
            username (str): Custom Instagram username
            
        Returns:
            bool: Success status
        """
        try:
            print(f"\n=== Phase 2 Custom Extraction ===")
            print(f"Extracting profile data from @{username}")
            
            success = self.extract_profile(username)
            
            if success:
                print(f"\n✅ Custom profile extraction completed for @{username}!")
                return True
            else:
                print(f"\n❌ Custom profile extraction failed for @{username}")
                return False
                
        except Exception as e:
            print(f"❌ Error during custom profile extraction: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.main_scraper:
                self.main_scraper.cleanup()
                print("🧹 Resources cleaned up")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def main():
    """Main entry point for Phase 2."""
    print("🚀 Instagram Profile Scraper - Phase 2: Profile Extraction")
    print("=" * 60)
    
    try:
        with Phase2InstagramScraper() as phase2:
            # Initialize
            if not phase2.initialize():
                print("❌ Initialization failed. Exiting...")
                return False
            
            # Check for command line arguments
            if len(sys.argv) > 1:
                username = sys.argv[1]
                success = phase2.run_phase2_custom(username)
            else:
                success = phase2.run_phase2_demo()
            
            if success:
                print(f"\n🎉 Phase 2 execution completed successfully!")
                return True
            else:
                print(f"\n💥 Phase 2 execution failed!")
                return False
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Process interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Critical error in Phase 2: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
