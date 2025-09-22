"""
User Interests Management Service
Handles storing and retrieving user interests from CSV files
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class UserInterestsService:
    """Service to manage user interests in CSV format"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.interests_file = os.path.join(self.data_dir, 'user_interests.csv')
        self.ensure_interests_file_exists()
    
    def ensure_interests_file_exists(self):
        """Ensure the user interests CSV file exists with proper headers"""
        if not os.path.exists(self.interests_file):
            # Create the file with headers
            df = pd.DataFrame(columns=[
                'Id', 'UserId', 'Topic', 'Interest', 'Location', 
                'Country', 'Timestamp', 'Source'
            ])
            df.to_csv(self.interests_file, index=False)
            logger.info(f"Created user interests file: {self.interests_file}")
    
    def load_interests(self) -> pd.DataFrame:
        """Load user interests from CSV file"""
        try:
            if os.path.exists(self.interests_file):
                df = pd.read_csv(self.interests_file)
                return df
            else:
                return pd.DataFrame(columns=[
                    'Id', 'UserId', 'Topic', 'Interest', 'Location', 
                    'Country', 'Timestamp', 'Source'
                ])
        except Exception as e:
            logger.error(f"Failed to load interests: {e}")
            return pd.DataFrame(columns=[
                'Id', 'UserId', 'Topic', 'Interest', 'Location', 
                'Country', 'Timestamp', 'Source'
            ])
    
    def save_interests(self, df: pd.DataFrame):
        """Save user interests to CSV file"""
        try:
            df.to_csv(self.interests_file, index=False)
            logger.info(f"Saved {len(df)} interest records")
        except Exception as e:
            logger.error(f"Failed to save interests: {e}")
    
    def add_user_interest(self, user_id: int, topic: str, interest: str, 
                         location: str = "", country: str = "", source: str = "trending") -> bool:
        """
        Add a new user interest record
        
        Args:
            user_id: User ID from users.csv
            topic: The topic name
            interest: 'interested' or 'not_interested'
            location: User's location
            country: Country code
            source: Source of the topic (e.g., 'trending', 'manual')
        """
        try:
            df = self.load_interests()
            
            # Get the next ID
            next_id = 1 if df.empty else df['Id'].max() + 1
            
            # Create new record
            new_record = {
                'Id': next_id,
                'UserId': user_id,
                'Topic': topic,
                'Interest': interest,
                'Location': location,
                'Country': country,
                'Timestamp': datetime.now().isoformat(),
                'Source': source
            }
            
            # Add to dataframe
            new_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to file
            self.save_interests(new_df)
            
            logger.info(f"Added interest for user {user_id}: {topic} -> {interest}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add user interest: {e}")
            return False
    
    def get_user_interests(self, user_id: int) -> List[Dict]:
        """Get all interests for a specific user"""
        try:
            df = self.load_interests()
            user_interests = df[df['UserId'] == user_id]
            
            return user_interests.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to get user interests: {e}")
            return []
    
    def get_user_interested_topics(self, user_id: int) -> List[str]:
        """Get topics the user is interested in"""
        try:
            df = self.load_interests()
            interested = df[(df['UserId'] == user_id) & (df['Interest'] == 'interested')]
            
            return interested['Topic'].tolist()
            
        except Exception as e:
            logger.error(f"Failed to get interested topics: {e}")
            return []
    
    def get_user_not_interested_topics(self, user_id: int) -> List[str]:
        """Get topics the user is not interested in"""
        try:
            df = self.load_interests()
            not_interested = df[(df['UserId'] == user_id) & (df['Interest'] == 'not_interested')]
            
            return not_interested['Topic'].tolist()
            
        except Exception as e:
            logger.error(f"Failed to get not interested topics: {e}")
            return []
    
    def has_user_responded_to_topic(self, user_id: int, topic: str) -> bool:
        """Check if user has already responded to a specific topic"""
        try:
            df = self.load_interests()
            existing = df[(df['UserId'] == user_id) & (df['Topic'] == topic)]
            
            return not existing.empty
            
        except Exception as e:
            logger.error(f"Failed to check topic response: {e}")
            return False
    
    def update_user_interest(self, user_id: int, topic: str, new_interest: str) -> bool:
        """Update an existing user interest"""
        try:
            df = self.load_interests()
            
            # Find existing record
            mask = (df['UserId'] == user_id) & (df['Topic'] == topic)
            
            if mask.any():
                # Update existing record
                df.loc[mask, 'Interest'] = new_interest
                df.loc[mask, 'Timestamp'] = datetime.now().isoformat()
                
                self.save_interests(df)
                logger.info(f"Updated interest for user {user_id}: {topic} -> {new_interest}")
                return True
            else:
                # No existing record, add new one
                return self.add_user_interest(user_id, topic, new_interest)
                
        except Exception as e:
            logger.error(f"Failed to update user interest: {e}")
            return False
    
    def get_popular_topics(self, limit: int = 10) -> List[Dict]:
        """Get most popular topics across all users"""
        try:
            df = self.load_interests()
            
            if df.empty:
                return []
            
            # Count interested responses by topic
            interested = df[df['Interest'] == 'interested']
            topic_counts = interested['Topic'].value_counts().head(limit)
            
            popular_topics = []
            for topic, count in topic_counts.items():
                popular_topics.append({
                    'topic': topic,
                    'interested_count': count
                })
            
            return popular_topics
            
        except Exception as e:
            logger.error(f"Failed to get popular topics: {e}")
            return []
    
    def get_user_interest_summary(self, user_id: int) -> Dict:
        """Get a summary of user's interests"""
        try:
            interests = self.get_user_interests(user_id)
            
            if not interests:
                return {
                    'total_responses': 0,
                    'interested_count': 0,
                    'not_interested_count': 0,
                    'interested_topics': [],
                    'not_interested_topics': [],
                    'latest_activity': None
                }
            
            interested_topics = [i['Topic'] for i in interests if i['Interest'] == 'interested']
            not_interested_topics = [i['Topic'] for i in interests if i['Interest'] == 'not_interested']
            
            # Get latest activity
            latest_activity = max(interests, key=lambda x: x['Timestamp'])['Timestamp']
            
            return {
                'total_responses': len(interests),
                'interested_count': len(interested_topics),
                'not_interested_count': len(not_interested_topics),
                'interested_topics': interested_topics,
                'not_interested_topics': not_interested_topics,
                'latest_activity': latest_activity
            }
            
        except Exception as e:
            logger.error(f"Failed to get user interest summary: {e}")
            return {
                'total_responses': 0,
                'interested_count': 0,
                'not_interested_count': 0,
                'interested_topics': [],
                'not_interested_topics': [],
                'latest_activity': None
            }

# Singleton instance
user_interests_service = UserInterestsService()