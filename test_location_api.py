#!/usr/bin/env python3
"""
Test Location API Endpoints
"""

import requests
import json

def test_location_endpoints():
    """Test the location API endpoints"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Location API Endpoints")
    print("=" * 50)
    
    # Test 1: Store Location
    print("\n📍 Test 1: Store Location API")
    test_location = {
        'latitude': 22.5726,
        'longitude': 88.3639,
        'accuracy': 100
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/store-location/",
            json=test_location,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Trending Topics API (Removed)
    print("\n🔥 Test 2: Trending Topics API - REMOVED")
    print("Trending topics endpoint has been removed due to dependency issues.")
    
    # Test 3: Init Chat
    print("\n💬 Test 3: Init Chat API")
    
    try:
        response = requests.post(
            f"{base_url}/api/init-chat/",
            json={
                'location': test_location,
                'trending_topics': ['Mental Health Awareness', 'Technology Innovation', 'Climate Change']
            },
            timeout=20
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Message: {result.get('message', 'No message')}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ API Endpoint Testing Complete")

if __name__ == "__main__":
    test_location_endpoints()