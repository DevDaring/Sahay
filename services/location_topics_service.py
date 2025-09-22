"""
Google Trends and Location-based Topics Service
Handles fetching trending topics based on user location
"""

import requests
import json
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import geocoder
import random

logger = logging.getLogger(__name__)

class LocationTopicsService:
    """Service to fetch trending topics based on user location"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_location_name(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to location name using reverse geocoding
        """
        try:
            # Using geocoder library for reverse geocoding
            location = geocoder.arcgis([latitude, longitude], method='reverse')
            
            if location.ok:
                # Try to get city, state, country
                city = location.city or ""
                state = location.state or ""
                country = location.country or ""
                
                if city and state:
                    return f"{city}, {state}"
                elif city and country:
                    return f"{city}, {country}"
                elif state and country:
                    return f"{state}, {country}"
                elif country:
                    return country
                    
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get location name: {e}")
            return None
    
    def get_country_code(self, latitude: float, longitude: float) -> str:
        """
        Get country code from coordinates
        """
        try:
            location = geocoder.arcgis([latitude, longitude], method='reverse')
            if location.ok and location.country_code:
                return location.country_code.upper()
            return 'US'  # Default fallback
        except Exception as e:
            logger.warning(f"Failed to get country code: {e}")
            return 'US'
    
    def fetch_google_trends_daily(self, location_name: str, country_code: str = 'US') -> List[str]:
        """
        Fetch Google Trends daily trending searches
        Using Google Trends RSS feed
        """
        try:
            # Google Trends daily RSS feed URL
            base_url = "https://trends.google.com/trends/trendingsearches/daily/rss"
            
            params = {
                'geo': country_code
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the RSS feed for trending topics
            topics = self._parse_trends_rss(response.text)
            
            if not topics:
                # Fallback to simulated trending topics
                topics = self._get_fallback_trends(location_name)
            
            logger.info(f"Fetched {len(topics)} trending topics for {location_name}")
            return topics[:5]  # Return top 5 trends
            
        except Exception as e:
            logger.warning(f"Failed to fetch Google Trends: {e}")
            return self._get_fallback_trends(location_name)
    
    def _parse_trends_rss(self, rss_content: str) -> List[str]:
        """
        Parse Google Trends RSS content to extract trending topics
        """
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(rss_content)
            topics = []
            
            # Look for item titles in RSS
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    # Clean up the title
                    title = title_elem.text.strip()
                    if title and len(title) < 100:  # Reasonable length check
                        topics.append(title)
            
            return topics[:10]  # Return top 10
            
        except Exception as e:
            logger.warning(f"Failed to parse RSS content: {e}")
            return []
    
    def fetch_simulated_trends(self, location_name: str) -> List[str]:
        """
        Fetch simulated trending topics based on location and current events
        This is a fallback when real API calls fail
        """
        
        # General trending categories
        categories = {
            'technology': [
                'Artificial Intelligence',
                'Electric Vehicles',
                'Cryptocurrency',
                'Remote Work',
                'Digital Health',
                'Climate Tech'
            ],
            'entertainment': [
                'Streaming Movies',
                'Concert Tours',
                'Gaming Updates',
                'Celebrity News',
                'Sports Events',
                'Music Releases'
            ],
            'health': [
                'Mental Health Awareness',
                'Healthy Lifestyle',
                'Fitness Trends',
                'Nutrition Tips',
                'Wellness Apps',
                'Meditation'
            ],
            'news': [
                'Climate Change',
                'Economic Updates',
                'Education Reform',
                'Local Events',
                'Community News',
                'Policy Changes'
            ]
        }
        
        # Location-specific adjustments
        location_specific = {
            'India': ['Cricket Updates', 'Bollywood News', 'Festival Celebrations'],
            'US': ['NFL Season', 'Election Updates', 'Tech Innovation'],
            'UK': ['Premier League', 'Royal Family', 'Brexit Impact'],
            'Canada': ['Hockey Season', 'Weather Updates', 'Healthcare News']
        }
        
        # Combine general and location-specific trends
        all_topics = []
        for category_topics in categories.values():
            all_topics.extend(category_topics)
        
        # Add location-specific topics if available
        for country, topics in location_specific.items():
            if country.lower() in location_name.lower():
                all_topics.extend(topics)
                break
        
        # Randomly select 5 topics
        selected_topics = random.sample(all_topics, min(5, len(all_topics)))
        
        logger.info(f"Generated simulated trends for {location_name}: {selected_topics}")
        return selected_topics
    
    def _get_fallback_trends(self, location_name: str) -> List[str]:
        """
        Fallback trending topics when all other methods fail
        """
        fallback_topics = [
            'Mental Health Awareness',
            'Climate Change Action',
            'Technology Innovation',
            'Community Events',
            'Wellness and Fitness'
        ]
        
        logger.info(f"Using fallback trends for {location_name}")
        return fallback_topics
    
    def get_trending_topics(self, latitude: float, longitude: float) -> Dict:
        """
        Main method to get trending topics based on coordinates
        """
        try:
            # Get location information
            location_name = self.get_location_name(latitude, longitude)
            country_code = self.get_country_code(latitude, longitude)
            
            if not location_name:
                location_name = f"Location ({latitude:.2f}, {longitude:.2f})"
            
            # Try to fetch real trends first, then fallback to simulated
            try:
                topics = self.fetch_google_trends_daily(location_name, country_code)
            except Exception as e:
                logger.warning(f"Google Trends failed, using simulated: {e}")
                topics = self.fetch_simulated_trends(location_name)
            
            # If still no topics, use fallback
            if not topics:
                topics = self._get_fallback_trends(location_name)
            
            return {
                'location': location_name,
                'country_code': country_code,
                'topics': topics,
                'timestamp': datetime.now().isoformat(),
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get trending topics: {e}")
            return {
                'location': 'Unknown Location',
                'country_code': 'US',
                'topics': self._get_fallback_trends('Unknown Location'),
                'timestamp': datetime.now().isoformat(),
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
    
    def get_topics_for_chat_init(self, trending_data: Dict, user_name: str = None) -> str:
        """
        Generate a personalized message about trending topics for chat initialization
        """
        location = trending_data.get('location', 'your area')
        topics = trending_data.get('topics', [])
        
        if not topics:
            return f"Hello{' ' + user_name if user_name else ''}! I'd love to chat with you today. What's on your mind?"
        
        # Select 2-3 most interesting topics
        selected_topics = topics[:3]
        
        # Create personalized message
        greeting = f"Hello{' ' + user_name if user_name else ''}! "
        
        if len(selected_topics) == 1:
            message = f"{greeting}I noticed that '{selected_topics[0]}' is trending in {location}. Are you interested in discussing this topic, or would you prefer to talk about something else that's on your mind today?"
        elif len(selected_topics) == 2:
            message = f"{greeting}I see that '{selected_topics[0]}' and '{selected_topics[1]}' are trending topics in {location}. Would you like to explore any of these, or is there something else you'd like to discuss?"
        else:
            topics_text = ', '.join(selected_topics[:-1]) + f", and {selected_topics[-1]}"
            message = f"{greeting}There are some interesting topics trending in {location} like {topics_text}. Would you like to chat about any of these, or is there something else on your mind?"
        
        return message

# Singleton instance
location_topics_service = LocationTopicsService()