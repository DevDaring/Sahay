#!/usr/bin/env python3
"""
Demo script showing Gemini AI integration with CSV data system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import GeminiService
from services.data_processing import CSVDataProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def demo_csv_gemini_integration():
    """Demonstrate Gemini AI working with CSV data"""
    print("🤖 Sahay Platform - CSV + Gemini AI Integration Demo")
    print("="*60)
    
    try:
        # Initialize services
        print("📊 Initializing CSV data processor...")
        csv_processor = CSVDataProcessor()
        
        print("🤖 Initializing Gemini AI service...")
        gemini = GeminiService()
        
        print("✅ Both services initialized successfully!")
        
        print_section("STUDENT PROFILE WITH AI GREETING")
        
        # Get a student from CSV data
        students = csv_processor.get_students()
        if not students.empty:
            student = students.iloc[0]
            student_profile = {
                "interests": student.get('interests', []),
                "language": student.get('language_pref', 'English'),
                "age_band": student.get('age_band', '18-22')
            }
            
            print(f"📋 Student Data from CSV: {student['student_id']}")
            print(f"   Age Band: {student_profile['age_band']}")
            print(f"   Language: {student_profile['language']}")
            print(f"   Interests: {student_profile['interests']}")
            
            # Generate AI greeting
            greeting = gemini.generate_greeting(student_profile)
            print(f"\n🎓 AI-Generated Personalized Greeting:")
            print(f"   {greeting}")
        
        print_section("WELLNESS DATA + AI RESPONSE")
        
        # Get wellness sessions from CSV
        wellness_sessions = csv_processor.get_wellness_sessions()
        if not wellness_sessions.empty:
            session = wellness_sessions.iloc[0]
            
            print(f"📈 Wellness Data from CSV:")
            print(f"   Student: {session['student_id']}")
            print(f"   Mood Score: {session['mood_score']}/10")
            print(f"   Anxiety Score: {session['anxiety_score']}/10")
            print(f"   Risk Level: {session['risk_level']}")
            
            # Generate AI wellness response
            ai_message = "I just completed my wellness check-in and wanted to talk about my results."
            wellness_response = gemini.generate_wellness_response(
                mood_score=session['mood_score'],
                anxiety_score=session['anxiety_score'],
                message=ai_message
            )
            print(f"\n💚 AI Wellness Response:")
            print(f"   {wellness_response}")
        
        print_section("COURSE DATA + AI STUDY TIPS")
        
        # Get course information directly from data
        if 'courses' in csv_processor.data and not csv_processor.data['courses'].empty:
            courses = csv_processor.data['courses']
            course = courses.iloc[0]  # Programming course
            
            print(f"📚 Course Data from CSV:")
            print(f"   Course: {course['course_id']} - {course['topic']}")
            print(f"   Difficulty: Level {course['difficulty_level']}")
            print(f"   Prerequisites: {course.get('prerequisites', [])}")
            
            # Generate AI study tips
            study_tips = gemini.generate_study_tips(
                topic=course['topic'],
                difficulty=f"Level {course['difficulty_level']}",
                challenge="Understanding the fundamental concepts"
            )
            print(f"\n📖 AI-Generated Study Tips:")
            print(f"   {study_tips}")
        
        print_section("CAREER PATH DATA + AI GUIDANCE")
        
        # Get career path information directly from data
        if 'career_paths' in csv_processor.data and not csv_processor.data['career_paths'].empty:
            career_paths = csv_processor.data['career_paths']
            current_path = career_paths.iloc[0]  # Software Engineering
            explore_path = career_paths.iloc[1] if len(career_paths) > 1 else career_paths.iloc[0]
            
            print(f"🎯 Career Data from CSV:")
            print(f"   Current Track: {current_path['field']}")
            print(f"   Exploring: {explore_path['field']}")
            
            # Get student interests from earlier
            student_interests = ["programming", "problem-solving", "technology"]
            
            # Generate AI career guidance
            career_advice = gemini.generate_career_advice(
                interests=student_interests,
                current_field=current_path['field'],
                explore_field=explore_path['field']
            )
            print(f"\n🚀 AI Career Guidance:")
            print(f"   {career_advice.get('summary', 'Focus on building core skills.')}")
            
            if career_advice.get('next_steps'):
                print(f"   Next Steps:")
                for step in career_advice['next_steps'][:3]:
                    print(f"     • {step}")
        
        print_section("REAL-TIME AI CHAT WITH CONTEXT")
        
        # Simulate a chat conversation with context from CSV data
        if not students.empty and not wellness_sessions.empty:
            student_id = students.iloc[0]['student_id']
            latest_session = wellness_sessions[wellness_sessions['student_id'] == student_id]
            
            if not latest_session.empty:
                session = latest_session.iloc[-1]  # Most recent session
                
                print(f"💬 Simulating chat for: {student_id}")
                print(f"   Recent wellness: Mood {session['mood_score']}/10, Anxiety {session['anxiety_score']}/10")
                
                # First message
                user_message1 = "Hi Sahay, I'm feeling stressed about my upcoming exams."
                context = {
                    "mood_score": session['mood_score'],
                    "anxiety_score": session['anxiety_score']
                }
                
                chat_response1 = gemini.process_chat_message(student_id, user_message1, context)
                print(f"\n   Student: {user_message1}")
                print(f"   Sahay: {chat_response1.get('response', 'No response')}")
                
                # Follow-up message
                user_message2 = "Can you suggest some specific study techniques for computer science?"
                chat_response2 = gemini.process_chat_message(student_id, user_message2)
                print(f"\n   Student: {user_message2}")
                print(f"   Sahay: {chat_response2.get('response', 'No response')}")
                
                # Risk analysis
                risk_level = chat_response1.get('risk_indicators', {}).get('level', 'none')
                print(f"\n🔍 AI Risk Analysis: {risk_level}")
                if risk_level != 'none':
                    suggested_actions = chat_response1.get('suggested_actions', [])
                    print(f"   Suggested Actions: {suggested_actions}")
        
        print_section("PERSONALIZED ACTIONS FROM DATA")
        
        # Generate personalized actions based on student data
        if not students.empty:
            student = students.iloc[0]
            interests = student.get('interests', [])
            
            # Use wellness data if available
            wellness_level = "medium"
            energy_level = 6
            if not wellness_sessions.empty:
                recent_session = wellness_sessions.iloc[0]
                mood = recent_session['mood_score']
                if mood >= 7:
                    wellness_level = "high"
                    energy_level = 8
                elif mood <= 4:
                    wellness_level = "low"
                    energy_level = 4
            
            print(f"⚡ Generating actions for student with:")
            print(f"   Interests: {interests}")
            print(f"   Wellness Level: {wellness_level}")
            print(f"   Energy Level: {energy_level}/10")
            
            actions = gemini.generate_personalized_actions(
                wellness_level=wellness_level,
                energy_level=energy_level,
                time_available=45,
                interests=interests if isinstance(interests, list) else ["learning"]
            )
            
            print(f"\n📋 AI-Generated Personalized Actions:")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action.get('action', 'Default action')}")
                print(f"      ⏱️ {action.get('duration', 15)} minutes | 📂 {action.get('category', 'general')}")
        
        print_section("INTEGRATION SUMMARY")
        print("✅ CSV Data + Gemini AI Integration Complete!")
        print()
        print("🔄 Integration Features Demonstrated:")
        print("   📊 CSV data provides student context and history")
        print("   🤖 Gemini AI generates personalized responses") 
        print("   💬 Chat maintains conversation history")
        print("   🔍 Risk analysis from student messages")
        print("   ⚡ Personalized actions based on data + AI")
        print("   🎯 Career guidance using both data sources")
        print()
        print("🚀 The system is ready for hackathon deployment!")
        print("   • No database dependency")
        print("   • Privacy-compliant CSV storage")
        print("   • Advanced AI-powered interactions")
        print("   • Real-time personalization")
        
    except Exception as e:
        logger.error(f"Integration demo failed: {e}")
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_csv_gemini_integration()
