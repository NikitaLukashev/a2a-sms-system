#!/usr/bin/env python3
"""
Basic Test for SMS Host Protocol
Tests basic functionality without external dependencies
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_environment():
    """Test environment configuration"""
    print("⚙️ Testing Environment Configuration...")
    
    required_vars = [
        "MISTRAL_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN", 
        "TWILIO_PHONE_NUMBER",
        "GUEST_PHONE_NUMBER"
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)}")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good

def test_file_structure():
    """Test that the file structure is correct"""
    print("📁 Testing File Structure...")
    
    # Check if main files exist
    main_files = [
        "main.py",
        "sms_handler.py", 
        "a2a_protocol.py",
        "ai_response_generator.py"
    ]
    
    all_exist = True
    for file in main_files:
        if Path(__file__).parent.parent / file:
            print(f"✓ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    # Check if config folder exists
    config_path = Path(__file__).parent.parent / "config"
    if config_path.exists():
        print("✓ config/ folder exists")
    else:
        print("❌ config/ folder missing")
        all_exist = False
    
    return all_exist

def main():
    """Run basic tests"""
    print("🚀 SMS Host Protocol - Basic Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 BASIC TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Basic tests passed! File structure is correct.")
        return 0
    else:
        print("⚠️  Some basic tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
