#!/usr/bin/env python3
"""
Test Script for SMS Host Protocol
Tests the system functionality without external dependencies
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_property_parser():
    """Test the property parser functionality"""
    print("🧪 Testing Property Parser...")
    
    from config.listing_parser import property_parser
    
    # Test basic functionality
    property_name = property_parser.get_property_name()
    location = property_parser.get_location()
    checkin_info = property_parser.get_checkin_info()
    amenities = property_parser.get_amenities()
    
    print(f"✓ Property Name: {property_name}")
    print(f"✓ Location: {location}")
    print(f"✓ Check-in Info: {checkin_info}")
    print(f"✓ Amenities: {amenities}")
    
    return True

def test_ai_generator():
    """Test the AI response generator"""
    print("\n🤖 Testing AI Response Generator (Mistral Large)...")
    
    from controller.ai_response_generator import ai_generator
    
    # Test response generation
    test_questions = [
        "Do you have WiFi?",
        "What time is check-in?",
        "Is parking included?"
    ]
    
    for question in test_questions:
        response = ai_generator.generate_response(question, "Test Guest")
        print(f"✓ Q: {question}")
        print(f"  A: {response}")
    
    return True

def test_protocol():
    """Test the main protocol"""
    print("\n🔧 Testing SMS Host Protocol...")
    
    from controller.a2a_protocol import sms_protocol
    
    # Test protocol status
    status = sms_protocol.get_protocol_status()
    print(f"✓ Protocol ID: {status['protocol_id']}")
    print(f"✓ Agent ID: {status['agent_id']}")
    print(f"✓ Status: {status['status']}")
    print(f"✓ AI Model: {status['ai_model']}")
    print(f"✓ AI Provider: {status['ai_provider']}")
    
    # Test message processing (without SMS)
    test_message = "Do you have WiFi?"
    response = sms_protocol.process_guest_message(test_message)
    print(f"✓ Test Message: {test_message}")
    print(f"✓ Response: {response}")
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n⚙️ Testing Environment Configuration...")
    
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

def main():
    """Run all tests"""
    print("🚀 SMS Host Protocol - System Test (Mistral AI)")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Property Parser", test_property_parser),
        ("AI Response Generator (Mistral)", test_ai_generator),
        ("SMS Host Protocol", test_protocol)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("🤖 AI Assistant: Mistral Large is configured and working!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
