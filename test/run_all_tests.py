#!/usr/bin/env python3
"""
Test Runner for SMS Host Protocol
Runs all tests in the test folder
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_file(test_file: str):
    """Run a specific test file"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
            print(result.stdout)
        else:
            print("❌ Test failed")
            print(result.stdout)
            if result.stderr:
                print("Error output:")
                print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SMS Host Protocol - Complete Test Suite")
    print("=" * 60)
    
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Find all test files
    test_files = [f for f in test_dir.glob("test_*.py") if f.name != "__init__.py"]
    
    if not test_files:
        print("❌ No test files found")
        return 1
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    print("\n💡 Note: Some tests may fail if external dependencies (Mistral API, Twilio) are not configured.")
    print("   This is expected in development environments without API keys.")
    
    # Run all tests
    results = []
    for test_file in test_files:
        success = run_test_file(str(test_file))
        results.append((test_file.name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed.")
        print("\n💡 This is normal if:")
        print("   - Environment variables are not set (.env file missing)")
        print("   - External APIs are not configured")
        print("   - Dependencies are not installed")
        print("\n✅ File structure and basic functionality tests should pass.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
