"""
Custom authentication backend for CSV-based user authentication
"""
import csv
import os
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings


class CSVAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend that validates users against a CSV file.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user against the CSV file.
        """
        if username is None or password is None:
            return None
            
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'users.csv')
        
        if not os.path.exists(csv_path):
            return None
            
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['UserName'] == username and row['Password'] == password:
                        # User found in CSV, create or get Django user
                        try:
                            user = User.objects.get(username=username)
                        except User.DoesNotExist:
                            # Create a new Django user
                            user = User.objects.create_user(
                                username=username,
                                email=username if '@' in username else f"{username}@example.com",
                                first_name=row.get('Name', '').split()[0] if row.get('Name') else '',
                                last_name=' '.join(row.get('Name', '').split()[1:]) if len(row.get('Name', '').split()) > 1 else ''
                            )
                        return user
        except Exception as e:
            # Log the error if needed
            print(f"CSV Authentication error: {e}")
            return None
            
        return None
    
    def get_user(self, user_id):
        """
        Get a user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None