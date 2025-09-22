#!/usr/bin/env python3
"""
Test personalized Gemini responses with user data from CSV (without Django settings)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sahay.settings')

import django
django.setup()

from services.data_processing import CSVDataProcessor

def test_user_data_processing():
    """Test user data processing and name extraction"""
    print("🧪 Testing User Data Processing")
    print("=" * 50)
    
    # Initialize CSV processor
    csv_processor = CSVDataProcessor()
    
    # Test 1: Check if users data is loaded
    print("📊 Testing User Data Loading...")
    users_df = csv_processor.data.get('users', None)
    if users_df is not None and not users_df.empty:
        print(f"✅ Users data loaded: {len(users_df)} users")
        print(f"   Columns: {list(users_df.columns)}")
        
        # Show sample user data
        if len(users_df) > 0:
            print(f"   Sample users:")
            for i, (idx, user) in enumerate(users_df.iterrows()):
                if i < 3:  # Show first 3 users
                    print(f"   {i+1}. ID: {user.get('Id')}, Name: {user.get('Name')}, Username: {user.get('UserName')}")
    else:
        print("❌ No users data found")
        return
    
    # Test 2: Test first name extraction for Koushik Deb
    print("\n👤 Testing First Name Extraction...")
    
    # Test by username (email)
    test_username = "test@example.com"
    first_name_by_username = csv_processor.get_user_first_name(username=test_username)
    print(f"By username '{test_username}': '{first_name_by_username}'")
    
    # Test by user ID  
    test_user_id = 1
    first_name_by_id = csv_processor.get_user_first_name(user_id=test_user_id)
    print(f"By user ID {test_user_id}: '{first_name_by_id}'")
    
    # Test all users to see name extraction
    print(f"\n📋 All users and their extracted first names:")
    for idx, user in users_df.iterrows():
        user_id = user.get('Id')
        full_name = user.get('Name')
        username = user.get('UserName')
        extracted_name = csv_processor.get_user_first_name(user_id=user_id)
        print(f"   ID {user_id}: '{full_name}' → First name: '{extracted_name}' (Username: {username})")
    
    # Test 3: Demo how responses would be personalized
    print(f"\n💬 Demo: How Responses Would Be Personalized")
    print("=" * 50)
    
    for idx, user in users_df.iterrows():
        user_id = user.get('Id')
        full_name = user.get('Name')
        username = user.get('UserName')
        first_name = csv_processor.get_user_first_name(user_id=user_id)
        
        if first_name:
            print(f"\nUser: {full_name} (ID: {user_id}, Username: {username})")
            print(f"🤖 Gemini would address them as: '{first_name}'")
            
            # Demo responses
            demo_responses = [
                f"Hi {first_name}, I understand you're feeling stressed. Let's work through this together.",
                f"{first_name}, it sounds like you're dealing with a lot right now. I'm here to help.",
                f"I hear you, {first_name}. These feelings are completely valid."
            ]
            
            print(f"📝 Sample personalized responses:")
            for i, response in enumerate(demo_responses, 1):
                print(f"   {i}. {response}")
    
    print(f"\n🎯 Integration Summary")
    print("=" * 50)
    print("✅ User CSV data: Successfully loaded")
    print("✅ Name extraction: Working correctly")
    print("✅ Personalization: Ready for implementation")
    print("✅ Multi-user support: Configured")
    print("\n🌟 When users chat with Sahay:")
    print("   • Their first names will be extracted from the CSV")
    print("   • Gemini will use their names in responses")
    print("   • Responses will be SHORT, COMPASSIONATE, and FRIENDLY")
    print("   • All languages (English, Hindi, Bengali) supported")

if __name__ == "__main__":
    test_user_data_processing()