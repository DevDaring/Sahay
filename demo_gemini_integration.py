#!/usr/bin/env python3
"""
Demo script to test the updated Gemini service integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import GeminiService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def demo_gemini_service():
    """Demonstrate the updated Gemini service capabilities"""
    print("🤖 Sahay Platform - Gemini AI Integration Demo")
    print("="*50)
    
    try:
        # Initialize Gemini service
        print("📡 Initializing Gemini service...")
        gemini = GeminiService()
        print("✅ Gemini service initialized successfully!")
        
        print_section("PERSONALIZED GREETING")
        
        # Demo student profile
        student_profile = {
            "interests": ["coding", "music", "reading"],
            "language": "English", 
            "age_band": "18-20"
        }
        
        print(f"Student Profile: {student_profile}")
        greeting = gemini.generate_greeting(student_profile)
        print(f"\n🎓 Sahay's Greeting:")
        print(f"   {greeting}")
        
        print_section("WELLNESS RESPONSE")
        
        # Demo wellness check
        mood_score = 6
        anxiety_score = 7
        message = "I'm feeling overwhelmed with my coursework and not sure if I can handle everything."
        
        print(f"Mood Score: {mood_score}/10")
        print(f"Anxiety Score: {anxiety_score}/10") 
        print(f"Student Message: \"{message}\"")
        
        wellness_response = gemini.generate_wellness_response(mood_score, anxiety_score, message)
        print(f"\n💚 Sahay's Wellness Response:")
        print(f"   {wellness_response}")
        
        print_section("STUDY SUPPORT")
        
        # Demo study tips
        topic = "Data Structures and Algorithms"
        difficulty = "intermediate"
        challenge = "Understanding time complexity analysis"
        
        print(f"Topic: {topic}")
        print(f"Difficulty: {difficulty}")
        print(f"Challenge: {challenge}")
        
        study_tips = gemini.generate_study_tips(topic, difficulty, challenge)
        print(f"\n📚 Sahay's Study Tips:")
        print(f"   {study_tips}")
        
        print_section("CAREER GUIDANCE")
        
        # Demo career advice
        interests = ["programming", "problem-solving", "technology"]
        current_field = "Computer Science"
        explore_field = "Data Science"
        
        print(f"Interests: {interests}")
        print(f"Current Field: {current_field}")
        print(f"Exploring: {explore_field}")
        
        career_advice = gemini.generate_career_advice(interests, current_field, explore_field)
        print(f"\n🎯 Sahay's Career Guidance:")
        print(f"   Summary: {career_advice.get('summary', 'No summary available')}")
        print(f"   Next Steps: {career_advice.get('next_steps', [])}")
        
        print_section("PERSONALIZED ACTIONS")
        
        # Demo action generation
        wellness_level = "medium"
        energy_level = 6
        time_available = 30
        interests = ["coding", "music"]
        
        print(f"Wellness Level: {wellness_level}")
        print(f"Energy Level: {energy_level}/10")
        print(f"Time Available: {time_available} minutes")
        print(f"Interests: {interests}")
        
        actions = gemini.generate_personalized_actions(wellness_level, energy_level, time_available, interests)
        print(f"\n⚡ Sahay's Recommended Actions:")
        for i, action in enumerate(actions, 1):
            print(f"   {i}. {action.get('action', 'No action')}")
            print(f"      Duration: {action.get('duration', 0)} mins | Category: {action.get('category', 'general')}")
        
        print_section("CHAT CONVERSATION")
        
        # Demo chat interaction
        student_id = "STU001"
        user_message = "I'm really struggling with my programming assignment and feel like giving up."
        context = {"mood_score": 4, "anxiety_score": 8}
        
        print(f"Student ID: {student_id}")
        print(f"Message: \"{user_message}\"")
        print(f"Context: {context}")
        
        chat_response = gemini.process_chat_message(student_id, user_message, context)
        print(f"\n💬 Sahay's Chat Response:")
        print(f"   {chat_response.get('response', 'No response')}")
        print(f"   Risk Level: {chat_response.get('risk_indicators', {}).get('level', 'none')}")
        
        # Follow-up message
        follow_up = "Thanks, that actually makes me feel a bit better. Can you help me break down the problem?"
        chat_response2 = gemini.process_chat_message(student_id, follow_up)
        print(f"\n💬 Follow-up Response:")
        print(f"   {chat_response2.get('response', 'No response')}")
        
        print_section("DEMO COMPLETE")
        print("✅ All Gemini AI features demonstrated successfully!")
        print("🔗 The service is now integrated with the new Google GenAI SDK")
        print("🚀 Ready for use in the Sahay platform!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_gemini_service()
