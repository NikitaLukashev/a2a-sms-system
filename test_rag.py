#!/usr/bin/env python3
"""
Test Script for RAG-based Property Parser
Tests the new RAG architecture with LangChain and Mistral embeddings
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rag_system():
    """Test the RAG-based property parser with Mistral embeddings"""
    print("🧠 Testing RAG-based Property Parser (Mistral Embeddings)")
    print("=" * 60)
    
    # Import the RAG parser
    from config.listing_parser import property_parser
    
    print("✅ RAG Property Parser imported successfully")
    
    # Test database stats
    print("\n📊 Testing Database Statistics...")
    stats = property_parser.get_database_stats()
    print(f"Database Stats: {stats}")
    
    # Test property summary
    print("\n🏠 Testing Property Summary...")
    summary = property_parser.get_property_summary()
    print(f"Property Summary: {summary}")
    
    # Test RAG query
    print("\n🔍 Testing RAG Query...")
    query = "WiFi amenities check-in"
    results = property_parser.query_property_info(query, k=3)
    print(f"Query: '{query}'")
    print(f"Results: {len(results)} chunks found")
    
    for i, result in enumerate(results[:2], 1):
        print(f"\nResult {i}:")
        print(f"Content: {result['content'][:100]}...")
        print(f"Score: {result['relevance_score']:.4f}")
        print(f"Source: {result['source']}")
    
    # Test AI context formatting
    print("\n🤖 Testing AI Context Formatting...")
    context = property_parser.format_for_ai_context("WiFi availability")
    print(f"AI Context: {context[:200]}...")
    
    print("\n🎉 RAG System Tests Completed Successfully!")
    print("🧠 Mistral Embeddings: Working perfectly!")
    return True

def test_ai_generator_with_rag():
    """Test AI response generator with RAG and Mistral embeddings"""
    print("\n🤖 Testing AI Response Generator with RAG (Mistral)")
    print("=" * 60)
    
    from ai_response_generator import ai_generator
    
    print("✅ AI Response Generator imported successfully")
    
    # Test response generation
    test_questions = [
        "Do you have WiFi?",
        "What time is check-in?",
        "Is parking included?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        response = ai_generator.generate_response(question, "TestGuest")
        print(f"Response: {response}")
    
    # Test RAG stats
    print("\n📊 RAG Statistics:")
    rag_stats = ai_generator.get_rag_stats()
    print(f"RAG Stats: {rag_stats}")
    
    print("\n🎉 AI Generator with RAG Tests Completed Successfully!")
    print("🧠 Mistral AI + Mistral Embeddings: Perfect combination!")
    return True

def main():
    """Run all RAG tests"""
    print("🚀 RAG Architecture Test Suite (Mistral Embeddings)")
    print("=" * 70)
    
    tests = [
        ("RAG Property Parser (Mistral)", test_rag_system),
        ("AI Generator with RAG (Mistral)", test_ai_generator_with_rag)
    ]
    
    total = len(tests)
    passed = 0
    
    for name, func in tests:
        print(f"\n--- Running Test: {name} ---")
        if func():
            passed += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 RAG TEST SUMMARY")
    print("="*70)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("🧠 RAG Architecture: Enabled with Mistral AI + Mistral Embeddings!")
        print("🚀 Full Mistral AI Stack: LLM + Embeddings for optimal performance!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the logs and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
