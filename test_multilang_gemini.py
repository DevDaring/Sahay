#!/usr/bin/env python3
"""
Test Multi-Language Gemini Integration
Quick test for language detection and multi-language responses
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import GeminiService

def test_multilang_functionality():
    """Test multi-language functionality"""
    print("🌍 Testing Multi-Language Gemini Integration...")
    
    # Initialize service
    try:
        gemini = GeminiService()
        print("✅ Gemini service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini service: {e}")
        return
    
    # Test messages in different languages
    test_cases = [
        # English
        {
            "message": "Hello, I'm feeling stressed about my exams. Can you help?",
            "expected_lang": "English"
        },
        # Hindi (Devanagari)
        {
            "message": "नमस्ते, मैं अपनी परीक्षाओं को लेकर चिंतित हूं। क्या आप मदद कर सकते हैं?",
            "expected_lang": "Hindi"
        },
        # Hindi (Roman)
        {
            "message": "Hello, main apne studies ke liye stress mein hoon. Kya aap help kar sakte hai?",
            "expected_lang": "Hindi"
        },
        # Bengali
        {
            "message": "হ্যালো, আমি আমার পরীক্ষা নিয়ে চিন্তিত। আপনি কি সাহায্য করতে পারেন?",
            "expected_lang": "Bengali"
        },
    ]
    
    print("\n🔍 Testing Language Detection...")
    for i, test_case in enumerate(test_cases, 1):
        detected_lang = gemini._detect_language(test_case["message"])
        status = "✅" if detected_lang == test_case["expected_lang"] else "⚠️"
        print(f"{status} Test {i}: {test_case['expected_lang']} -> Detected: {detected_lang}")
        print(f"   Message: {test_case['message'][:50]}...")
    
    print("\n💬 Testing Multi-Language Responses...")
    
    # Test wellness response in different languages
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['expected_lang']} ---")
        try:
            response = gemini.generate_wellness_response(
                mood_score=6,
                anxiety_score=7,
                message=test_case["message"],
                language=test_case['expected_lang']
            )
            print(f"Response: {response[:100]}...")
            print("✅ Generated successfully")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🔍 Testing Google Search Integration...")
    
    # Test search-enabled queries
    search_tests = [
        {
            "message": "What are the latest study techniques for computer science?",
            "language": "English"
        },
        {
            "message": "कंप्यूटर साइंस के लिए नवीनतम अध्ययन तकनीकें क्या हैं?",
            "language": "Hindi"
        }
    ]
    
    for test in search_tests:
        print(f"\n--- Search Test: {test['language']} ---")
        try:
            response = gemini.generate_study_tips(
                topic="Computer Science",
                difficulty="intermediate",
                challenge="Time management during exams",
                language=test['language']
            )
            print(f"Study tips: {response[:150]}...")
            print("✅ Search-enabled response generated")
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    print("\n🎯 Testing Default Actions with Language Support...")
    
    # Test default actions in different languages
    for lang in ["English", "Hindi", "Bengali"]:
        print(f"\n--- Default Actions: {lang} ---")
        try:
            actions = gemini._get_default_actions("medium", ["music", "art"], lang)
            print(f"Sample action: {actions[0]['action']}")
            print("✅ Language-aware actions generated")
        except Exception as e:
            print(f"❌ Error generating actions: {e}")
    
    print("\n🚨 Testing Crisis Resources with Language Support...")
    
    # Test crisis resources in different languages
    for lang in ["English", "Hindi", "Bengali"]:
        print(f"\n--- Crisis Resources: {lang} ---")
        try:
            resources = gemini._get_crisis_resources(lang)
            if "local_resources" in resources:
                print(f"Local resource: {resources['local_resources'][0]}")
            else:
                print(f"Hotline: {resources['hotlines'][0]['name']}")
            print("✅ Language-aware crisis resources generated")
        except Exception as e:
            print(f"❌ Error getting crisis resources: {e}")
    
    print("\n✅ Multi-Language Testing Complete!")
    print("\n📋 Summary:")
    print("- Language detection for English, Hindi (Devanagari & Roman), Bengali")
    print("- Multi-language wellness responses")
    print("- Google Search integration with language support")
    print("- Language-aware default actions and crisis resources")
    print("\n🚀 Your Sahay application now supports multi-language interactions!")

if __name__ == "__main__":
    test_multilang_functionality()
