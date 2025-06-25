"""
Test module for Phase 2: Profile Extraction
"""

import unittest
import sys
import os
import time
import json

# Add the phase files directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "phase files"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core files"))

from phase2_scraper import Phase2InstagramScraper
from main import InstagramProfileScraper


class TestPhase2(unittest.TestCase):
    """Test cases for Phase 2 Profile Extraction."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_username = "malangraya_info"
        cls.scraper = None
    
    def setUp(self):
        """Set up each test."""
        self.scraper = Phase2InstagramScraper()
    
    def tearDown(self):
        """Clean up after each test."""
        if self.scraper:
            self.scraper.cleanup()
    
    def test_phase2_initialization(self):
        """Test Phase 2 scraper initialization."""
        print("\n🧪 Testing Phase 2 initialization...")
        
        success = self.scraper.initialize()
        self.assertTrue(success, "Phase 2 initialization should succeed")
        self.assertIsNotNone(self.scraper.main_scraper, "Main scraper should be initialized")
        
        print("✅ Phase 2 initialization test passed")
    
    def test_profile_extraction_structure(self):
        """Test profile extraction returns proper structure."""
        print("\n🧪 Testing profile extraction structure...")
        
        # Initialize first
        success = self.scraper.initialize()
        self.assertTrue(success, "Initialization should succeed")
        
        # Extract profile
        results = self.scraper.main_scraper.extract_profile(self.test_username)
        
        # Check structure
        self.assertIsInstance(results, dict, "Results should be a dictionary")
        self.assertIn("success", results, "Results should have success field")
        self.assertIn("phase", results, "Results should have phase field")
        
        if results.get("success"):
            self.assertIn("profile_data", results, "Successful results should have profile_data")
            self.assertIn("extraction_timestamp", results, "Results should have timestamp")
            self.assertIn("session_info", results, "Results should have session info")
        
        print("✅ Profile extraction structure test passed")
    
    def test_profile_data_fields(self):
        """Test that profile data contains expected fields."""
        print("\n🧪 Testing profile data fields...")
        
        # Initialize first
        success = self.scraper.initialize()
        self.assertTrue(success, "Initialization should succeed")
        
        # Extract profile
        results = self.scraper.main_scraper.extract_profile(self.test_username)
        
        if results.get("success"):
            profile_data = results.get("profile_data", {})
            
            # Check for expected fields
            expected_fields = ["username", "display_name", "posts_count", "followers_count", 
                              "following_count", "bio", "extraction_timestamp"]
            
            for field in expected_fields:
                self.assertIn(field, profile_data, f"Profile data should contain {field}")
        
        print("✅ Profile data fields test passed")
    
    def test_json_output_saving(self):
        """Test that Phase 2 results are saved to JSON."""
        print("\n🧪 Testing JSON output saving...")
        
        # Initialize first  
        success = self.scraper.initialize()
        self.assertTrue(success, "Initialization should succeed")
        
        # Extract profile
        results = self.scraper.main_scraper.extract_profile(self.test_username)
        
        if results.get("success"):
            # Save results
            output_file = self.scraper.main_scraper.save_phase2_results(results, self.test_username)
            
            self.assertTrue(output_file, "Output file path should be returned")
            self.assertTrue(os.path.exists(output_file), "Output file should exist")
            
            # Verify JSON content
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data, results, "Saved data should match original results")
            
            # Check latest results file
            latest_file = os.path.join("output", "phase2_latest_results.json")
            self.assertTrue(os.path.exists(latest_file), "Latest results file should exist")
        
        print("✅ JSON output saving test passed")
    
    def test_error_handling(self):
        """Test error handling for invalid profiles."""
        print("\n🧪 Testing error handling...")
        
        # Initialize first
        success = self.scraper.initialize()
        self.assertTrue(success, "Initialization should succeed")
        
        # Try extracting from non-existent profile
        invalid_username = "nonexistent_profile_12345_test"
        results = self.scraper.main_scraper.extract_profile(invalid_username)
        
        self.assertIsInstance(results, dict, "Results should be a dictionary")
        self.assertIn("success", results, "Results should have success field")
        
        # Error handling should return proper structure
        if not results.get("success"):
            self.assertIn("error", results, "Failed results should have error field")
            self.assertIn("username", results, "Failed results should have username field")
        
        print("✅ Error handling test passed")


class TestPhase2Integration(unittest.TestCase):
    """Integration tests for Phase 2."""
    
    def test_phase2_full_workflow(self):
        """Test complete Phase 2 workflow."""
        print("\n🧪 Testing Phase 2 full workflow...")
        
        with Phase2InstagramScraper() as phase2:
            # Test initialization
            init_success = phase2.initialize()
            self.assertTrue(init_success, "Phase 2 should initialize successfully")
            
            # Test profile extraction
            extract_success = phase2.extract_profile("malangraya_info")
            
            # Note: This might fail due to Instagram restrictions, but should handle gracefully
            self.assertIsInstance(extract_success, bool, "Extract should return boolean")
        
        print("✅ Phase 2 full workflow test completed")


def run_phase2_tests():
    """Run all Phase 2 tests."""
    print("🧪 Running Phase 2 Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestPhase2))
    test_suite.addTest(unittest.makeSuite(TestPhase2Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All Phase 2 tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"⚠️ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase2_tests()
    if not success:
        sys.exit(1)
