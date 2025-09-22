#!/usr/bin/env python
"""
Test script for CSV authentication
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sahay.settings')
django.setup()

from django.contrib.auth import authenticate
from core.auth_backends import CSVAuthenticationBackend

def test_csv_authentication():
    """Test CSV authentication with test credentials"""
    print("Testing CSV Authentication...")
    
    # Test with correct credentials
    user = authenticate(username='test@example.com', password='My Secret')
    if user:
        print(f"✅ Authentication successful! User: {user.username}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Is authenticated: {user.is_authenticated}")
    else:
        print("❌ Authentication failed with correct credentials")
    
    print()
    
    # Test with wrong credentials
    user = authenticate(username='test@example.com', password='My Secret')
    if user:
        print("❌ Authentication succeeded with wrong password - this shouldn't happen")
    else:
        print("✅ Authentication correctly failed with wrong password")
    
    print()
    
    # Test with non-existent user
    user = authenticate(username='nonexistent@example.com', password='My Secret')
    if user:
        print("❌ Authentication succeeded with non-existent user - this shouldn't happen")
    else:
        print("✅ Authentication correctly failed with non-existent user")

if __name__ == '__main__':
    test_csv_authentication()