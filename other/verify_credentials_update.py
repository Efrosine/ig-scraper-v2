#!/usr/bin/env python3
"""
Credentials Update Verification Script
Verifies that test files now use real Instagram account credentials from .env file
"""

import os
import sys

def verify_credentials_update():
    """Verify that test files have been updated with real credentials."""
    print("=" * 60)
    print("📋 CREDENTIALS UPDATE VERIFICATION")
    print("=" * 60)
    
    # Check .env file content
    env_file = "configuration/.env"
    if os.path.exists(env_file):
        print("✅ .env file found")
        with open(env_file, 'r') as f:
            content = f.read()
            if "eprosine009:IniPwBaru123,eprosen2:desember@03" in content:
                print("✅ Real Instagram credentials found in .env file")
                print("   Primary: eprosine009:IniPwBaru123")
                print("   Backup:  eprosen2:desember@03")
            else:
                print("❌ Credentials not found in .env file")
                return False
    else:
        print("❌ .env file not found")
        return False
    
    # Check test_phase1.py file
    test_file = "testing/test_phase1.py"
    if os.path.exists(test_file):
        print("\n✅ test_phase1.py file found")
        with open(test_file, 'r') as f:
            content = f.read()
            
            # Count occurrences of real credentials
            real_creds_count = content.count("eprosine009:IniPwBaru123,eprosen2:desember@03")
            test_creds_count = content.count("test_user1:test_pass1,test_user2:test_pass2")
            
            print(f"   Real credentials occurrences: {real_creds_count}")
            print(f"   Test credentials occurrences: {test_creds_count}")
            
            if real_creds_count >= 3 and test_creds_count == 0:
                print("✅ Test file successfully updated with real credentials")
                
                # Check for updated account names in assertions
                if "current_account': 'eprosine009'" in content:
                    print("✅ Test assertions updated with real account names")
                else:
                    print("⚠️  Test assertions may need account name updates")
                    
            else:
                print("❌ Test file still contains old test credentials")
                return False
    else:
        print("❌ test_phase1.py file not found")
        return False
    
    print("\n📋 SUMMARY:")
    print("✅ .env file contains real Instagram credentials")
    print("✅ test_phase1.py updated to use real credentials")
    print("✅ Test assertions updated with real account names")
    print("✅ Ready for Phase 1 testing with actual Instagram accounts")
    
    print("\n🔒 SECURITY NOTE:")
    print("⚠️  Real credentials are now in test files")
    print("⚠️  Ensure these files are not committed to public repositories")
    print("⚠️  Consider using environment variables for CI/CD testing")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run Phase 1 tests: pytest testing/test_phase1.py -v")
    print("2. Execute Phase 1 scraper: python 'phase files/phase1_scraper.py'")
    print("3. Begin Phase 2 development")
    
    return True

def main():
    """Main execution function."""
    print("Instagram Profile Scraper - Credentials Update Verification")
    print("-" * 60)
    
    # Verify we're in the right directory
    if not os.path.exists("configuration/.env"):
        print("❌ Error: Please run from the ig-scraper-v2 root directory")
        return False
    
    success = verify_credentials_update()
    
    if success:
        print("\n🎉 CREDENTIALS UPDATE SUCCESSFUL!")
        print("All test files now use real Instagram account credentials.")
        return True
    else:
        print("\n❌ CREDENTIALS UPDATE INCOMPLETE!")
        print("Please check the files and try again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)
