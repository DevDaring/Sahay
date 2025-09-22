"""
services/gemini_service.py - Gemini AI Integration for Sahay (Updated for CSV-based system)
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import google.generativeai as genai
from django.utils import timezone

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service class for interacting with Google's Gemini AI model
    """
    
    def __init__(self, project_id: str = "My Secret", location: str = "us-central1"):
        """Initialize Gemini client with API key"""
        try:
            # Get API key from Django settings
            from django.conf import settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            
            if api_key:
                # Configure the generative AI client with API key
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            else:
                raise ValueError("GEMINI_API_KEY not found in settings")
            
            # Model configuration
            self.model_name = "gemini-2.5-flash"
            
            # Generation configuration
            self.generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=2048,
            )
            
            # Safety settings
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            # Store active chat histories (simplified for CSV-based system)
            self.chat_histories = {}
            
            # Load prompt templates
            self.prompts = self._load_prompts()
            
            logger.info("Gemini service initialized successfully with Gemini 2.5 Flash")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise
    
    def generate_location_based_greeting(self, trending_topics: List[str], location: str, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Generate a location-based greeting with trending topics for chat initialization"""
        try:
            # Get user's first name for personalization
            first_name = ""
            if username or user_id:
                from services.data_processing import CSVDataProcessor
                csv_processor = CSVDataProcessor()
                first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            
            # Create the trending topics text
            if trending_topics and len(trending_topics) > 0:
                if len(trending_topics) == 1:
                    topics_text = f"'{trending_topics[0]}'"
                elif len(trending_topics) == 2:
                    topics_text = f"'{trending_topics[0]}' and '{trending_topics[1]}'"
                else:
                    topics_text = "', '".join(trending_topics[:-1]) + f"', and '{trending_topics[-1]}'"
            else:
                topics_text = ""
            
            # Create personalized location-based greeting
            greeting_name = f"{first_name}, " if first_name else ""
            
            if topics_text:
                system_context = f"""You are Sahay, a compassionate and supportive wellness companion for students.

TASK: Create a warm, friendly greeting that mentions trending topics in the user's location.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's location: {location}
- Trending topics: {topics_text}
- Response language: {language}

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and warm in tone
- Be FRIENDLY and approachable
- {f"Use {first_name}'s name naturally" if first_name else "Use a friendly greeting"}
- Mention 1-2 of the trending topics
- Ask if they're interested in discussing these topics or something else
- Respond in {language}

EXAMPLE STYLE: "Hello {first_name if first_name else '[name]'}, I noticed that [topic] is trending in [location]. Are you interested in discussing this, or is there something else on your mind today?"

Generate a personalized greeting now:"""
            else:
                # Fallback when no trending topics
                system_context = f"""You are Sahay, a compassionate and supportive wellness companion for students.

TASK: Create a warm, friendly greeting.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's location: {location}
- Response language: {language}

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and warm in tone
- Be FRIENDLY and approachable
- {f"Use {first_name}'s name naturally" if first_name else "Use a friendly greeting"}
- Ask how they're feeling or what's on their mind
- Respond in {language}

Generate a personalized greeting now:"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating location-based greeting: {e}")
            # Fallback greeting
            greeting_name = f" {first_name}" if first_name else ""
            return self._get_fallback_greeting(greeting_name, language)
    
    def _get_fallback_greeting(self, name: str = "", language: str = "English") -> str:
        """Fallback greeting when location-based greeting fails"""
        fallback_greetings = {
            "English": f"Hello{name}! I'm Sahay, your AI wellness companion. I'm here to support your mental health and well-being. How are you feeling today?",
            "Hindi": f"नमस्ते{name}! मैं साहाय हूँ, आपका AI कल्याण साथी। मैं आपके मानसिक स्वास्थ्य और कल्याण का समर्थन करने के लिए यहाँ हूँ। आज आप कैसा महसूस कर रहे हैं?",
            "Bengali": f"হ্যালো{name}! আমি সাহায্য, আপনার AI কল্যাণ সঙ্গী। আমি আপনার মানসিক স্বাস্থ্য এবং সুস্থতা সমর্থন করতে এখানে আছি। আজ আপনি কেমন অনুভব করছেন?"
        }
        
        return fallback_greetings.get(language, fallback_greetings["English"])

    def generate_personalized_greeting(self, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Generate a personalized greeting using user's name and interests"""
        try:
            from services.data_processing import CSVDataProcessor
            csv_processor = CSVDataProcessor()
            
            # Get user information
            first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            hometown = csv_processor.get_user_hometown(username=username, user_id=user_id)
            course = csv_processor.get_user_course(username=username, user_id=user_id)
            interests = csv_processor.get_user_interests(username=username, user_id=user_id)
            
            # Create personalized greeting prompt
            name_part = f"{first_name}, " if first_name else ""
            
            system_context = f"""You are Sahay, a compassionate and supportive wellness companion for students in India.

TASK: Create a warm, personalized greeting that DISCOVERS interests based on hometown/local context FIRST, then gradually connects to their studies.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's hometown: {hometown if hometown else "Not provided"}
- User's course: {course if course else "Not provided"}
- User's interests: {interests if interests else "Not provided"}
- Response language: {language}

CONVERSATION FLOW:
1. START with hometown-based interest discovery
2. DON'T immediately connect course with interests
3. Let the user confirm their interests first
4. Then in follow-up conversations, suggest career connections

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and warm in tone
- Be FRIENDLY and approachable like a close friend
- Use ONLY the user's name (NO "from city" format)
- FOCUS on hometown/local culture and interests FIRST
- Show LOCAL KNOWLEDGE about their hometown
- ALWAYS end with an engaging question - THIS IS MANDATORY
- Respond in {language}
- NEVER end with a statement - ALWAYS end with a question mark

HOMETOWN-BASED INTEREST DISCOVERY EXAMPLES:
- Kolkata: "Kolkata is such a vibrant city with incredible football culture and literary heritage! Are you more drawn to the excitement of the East Bengal-Mohun Bagan rivalry, or do you find yourself lost in the works of Tagore and other Bengali writers?"
- Mumbai: "Mumbai has such an amazing mix of cricket passion and Bollywood creativity! Do you find yourself more captivated by the energy of Wankhede Stadium or the storytelling magic of Indian cinema?"
- Delhi: "Delhi is a city of contrasts - from the poetry of Old Delhi to the tech innovation of Gurgaon! What draws you more - the rich cultural heritage or the cutting-edge technology scene?"
- Bangalore: "Bangalore is India's tech capital with such a vibrant startup culture! Are you more excited about the innovative tech scene or the city's beautiful gardens and cultural diversity?"

CRITICAL: Your response MUST end with a question mark (?). No exceptions.

Generate a personalized greeting that discovers interests based on hometown and end with a question:"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating personalized greeting: {e}")
            # Fallback greeting
            first_name = ""
            if username or user_id:
                from services.data_processing import CSVDataProcessor
                csv_processor = CSVDataProcessor()
                first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            
            greeting_name = f" {first_name}" if first_name else ""
            return self._get_fallback_greeting(greeting_name, language)
    
    def ask_trivia_and_discover_interests(self, message: str, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Ask trivia questions based on hometown and interests, then discover new interests"""
        try:
            from services.data_processing import CSVDataProcessor
            csv_processor = CSVDataProcessor()
            
            # Get user information
            first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            hometown = csv_processor.get_user_hometown(username=username, user_id=user_id)
            course = csv_processor.get_user_course(username=username, user_id=user_id)
            current_interests = csv_processor.get_user_interests(username=username, user_id=user_id)
            
            # Check if user is discussing mental health/stress/anxiety topics
            mental_health_keywords = [
                'stressed', 'stress', 'anxious', 'anxiety', 'worried', 'worry', 'depressed', 'depression',
                'overwhelmed', 'tired', 'exhausted', 'burnout', 'mental health', 'feeling down', 'sad',
                'lonely', 'isolated', 'panic', 'panic attack', 'mood', 'emotional', 'therapy', 'counseling'
            ]
            message_lower = message.lower()
            is_mental_health_topic = any(keyword in message_lower for keyword in mental_health_keywords)
            
            # Check if user is discussing study/academic topics
            study_keywords = [
                'study', 'studying', 'studies', 'exam', 'exams', 'test', 'tests', 'assignment', 'assignments',
                'homework', 'project', 'projects', 'coursework', 'academic', 'grades', 'marks', 'performance',
                'learning', 'concentration', 'focus', 'memory', 'retention', 'understanding', 'concept', 'concepts',
                'subject', 'subjects', 'syllabus', 'curriculum', 'lecture', 'lectures', 'notes', 'revision'
            ]
            is_study_topic = any(keyword in message_lower for keyword in study_keywords)
            
            # Route to appropriate function based on topic
            if is_mental_health_topic:
                logger.info(f"Routing to mental wellbeing support for user {username}")
                return self.mental_wellbeing(message, username, user_id, language)
            elif is_study_topic:
                logger.info(f"Routing to study guide support for user {username}")
                return self.study_guide(message, username, user_id, language)
            
            # Check if user is expressing disinterest
            disinterest_keywords = ['not interested', 'not into', 'don\'t like', 'don\'t enjoy', 'not my thing', 'not for me']
            message_lower = message.lower()
            is_disinterest = any(keyword in message_lower for keyword in disinterest_keywords)
            
            if is_disinterest:
                # User expressed disinterest, ask what they love instead
                system_context = f"""You are Sahay, a compassionate wellness companion. The user has expressed disinterest in something.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's hometown: {hometown if hometown else "Not provided"}
- User's course: {course if course else "Not provided"}
- User's current interests: {current_interests if current_interests else "None"}
- User's message: {message}
- Response language: {language}

TASK:
1. Acknowledge their disinterest respectfully
2. Ask what they love or are passionate about instead
3. CONNECT their academic course with potential interests
4. Be curious and encouraging
5. Keep the conversation flowing naturally

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and understanding
- Be FRIENDLY and curious
- CONNECT their studies with interests when possible
- Respond in {language}
- Ask an open-ended question about what they love
- ALWAYS end with a question mark (?) - THIS IS MANDATORY

CRITICAL: Your response MUST end with a question mark (?). No exceptions.

Generate a response that asks what they're passionate about:"""
            else:
                    # Regular trivia and interest discovery
                    system_context = f"""You are Sahay, a compassionate wellness companion who talks like a close friend. Your task is to be HIGHLY ENGAGING and ask deep, specific questions about the user's interests with LOCAL KNOWLEDGE.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's hometown: {hometown if hometown else "Not provided"}
- User's course: {course if course else "Not provided"}
- User's current interests: {current_interests if current_interests else "None"}
- User's message: {message}
- Response language: {language}

CONVERSATION FLOW:
1. FIRST: Discover and explore their interests deeply
2. THEN: If they show strong interest (passionate, want to learn more, career interest), suggest career connections
3. FINALLY: Bridge their studies with confirmed interests

STRONG INTEREST INDICATORS:
- "passionate", "love", "really interested", "want to learn more"
- "career", "job", "work", "profession", "analytics", "tech", "programming"
- "study", "learn", "explore", "develop", "build"

TASK:
1. Show LOCAL KNOWLEDGE about their hometown and interests
2. Ask SPECIFIC, engaging questions that show genuine curiosity
3. Be like a friend who really wants to know them better
4. ALWAYS end with a question
5. Use local references when relevant
6. If user shows STRONG INTEREST, suggest how their course can connect to their passion

WHEN TO SUGGEST CAREER CONNECTIONS:
- User says: "passionate", "love", "really interested", "want to learn more"
- User mentions: "career", "job", "work", "profession", "analytics", "tech", "programming"
- User shows: "study", "learn", "explore", "develop", "build"

COURSE-INTEREST CONNECTION EXAMPLES (use when strong interest detected):
- Computer Science + Football: "Did you know that many famous computer scientists were also athletes? Sports analytics is revolutionizing how teams analyze player movements! Your B.Tech CS skills could help you build the next big sports analytics platform!"
- Computer Science + Writing: "The best programmers are often great storytellers! Code is like poetry - it needs to be elegant and readable. Your CS background could help you create interactive storytelling platforms!"
- Computer Science + Science Fiction: "Asimov's Foundation series inspired many computer scientists! His ideas about psychohistory are like predictive algorithms. You could actually build the AI systems you read about!"
- Engineering + Cricket: "Engineering principles are used in cricket analytics - from ball tracking to performance optimization! Your technical skills could revolutionize how cricket is analyzed!"
- Engineering + Reading: "Great engineers are voracious readers! Problem-solving skills come from understanding diverse perspectives. Your engineering mindset could help you create innovative educational platforms!"

LOCAL KNOWLEDGE EXAMPLES:
- Kolkata + literature: "I really love Rabindranath Tagore's works! Have you read Gitanjali?"
- Kolkata + football: "The East Bengal-Mohun Bagan rivalry is legendary! Which side do you support?"
- Kolkata + cricket: "The Eden Gardens atmosphere is incredible! Have you been there for a match?"
- Mumbai + cricket: "The Wankhede Stadium atmosphere is incredible! Have you been there?"
- Delhi + poetry: "Delhi's poetry scene is so vibrant! Do you attend poetry readings?"

SPECIFIC QUESTIONS BY INTEREST:
- Reading/novels: "What type of novels do you enjoy most? Who's your favorite author? What's the last book that really moved you?"
- Cricket: "What's your favorite team? Which player do you admire most? Have you been to Eden Gardens? What draws you to this sport?"
- Football: "What's your favorite team? Which player do you admire most? What draws you to this sport?"
- Cooking: "What's your signature dish? Do you prefer traditional recipes or experimenting?"

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and warm in tone
- Be FRIENDLY and approachable like a close friend
- Show LOCAL KNOWLEDGE when relevant
- ALWAYS end with an engaging question - THIS IS MANDATORY
- Respond in {language}
- Show genuine curiosity about their interests
- NEVER end with a statement - ALWAYS end with a question mark

CRITICAL: Your response MUST end with a question mark (?). No exceptions.

Generate a response that shows local knowledge and asks engaging, specific questions:"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract new interests and detect disinterest
            removed_interests = self._detect_disinterest(message, current_interests)
            new_interests = self._extract_interests_from_conversation(message, hometown, current_interests)
            
            # If user is expressing disinterest, don't add new interests that conflict
            if removed_interests and new_interests:
                # Check if the new interest is the same as what they're expressing disinterest in
                removed_list = [r.strip().lower() for r in removed_interests.split(',')]
                new_list = [n.strip().lower() for n in new_interests.split(',')]
                
                # Remove conflicting interests from new interests
                filtered_new_interests = []
                for new_interest in new_list:
                    if new_interest not in removed_list:
                        filtered_new_interests.append(new_interest)
                
                new_interests = ', '.join(filtered_new_interests) if filtered_new_interests else ""
            
            logger.info(f"Extracted interests from message '{message}': '{new_interests}'")
            logger.info(f"Detected disinterest: '{removed_interests}'")
            logger.info(f"Current interests: '{current_interests}'")
            
            # Update interests in CSV
            updated_interests = current_interests
            
            # Remove disinterested interests
            if removed_interests:
                updated_interests = self._remove_interests_from_string(updated_interests, removed_interests)
                logger.info(f"Removed interests: {removed_interests}")
            
            # Add new interests (only if not expressing disinterest)
            if new_interests:
                if updated_interests:
                    updated_interests = f"{updated_interests}, {new_interests}"
                else:
                    updated_interests = new_interests
                logger.info(f"Added new interests: {new_interests}")
            
            # Update CSV if interests changed
            if updated_interests != current_interests:
                success = csv_processor.update_user_interests(username=username, user_id=user_id, interests=updated_interests)
                logger.info(f"Updated interests for user {username}: {updated_interests}, Success: {success}")
            else:
                logger.info(f"No interest changes detected from message: '{message}'")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in trivia and interest discovery: {e}")
            return f"I'm here to listen and learn about you! Tell me more about what you enjoy doing."
    
    def _extract_interests_from_conversation(self, message: str, hometown: str, current_interests: str) -> str:
        """Extract interests from conversation with location context"""
        message_lower = message.lower()
        discovered_interests = []
        
        # Comprehensive interest keywords - more specific categories
        interest_keywords = {
            'poetry': ['poetry', 'poem', 'poet', 'verse', 'rhyme', 'jibanananda das', 'rabindranath tagore'],
            'music': ['music', 'song', 'singing', 'instrument', 'guitar', 'piano', 'classical', 'rock', 'pop'],
            'art': ['art', 'painting', 'drawing', 'sketch', 'canvas', 'artist', 'gallery'],
            'reading': ['reading', 'book', 'novel', 'novels', 'literature', 'author', 'library', 'read'],
            'science fiction': ['science fiction', 'sci-fi', 'sf', 'asimov', 'foundation', 'space', 'futuristic', 'robots', 'ai'],
            'football': ['football', 'soccer', 'east bengal', 'mohun bagan', 'derby', 'maidan'],
            'cricket': ['cricket', 'eden gardens', 'ipl', 'test match'],
            'tennis': ['tennis'],
            'basketball': ['basketball'],
            'swimming': ['swimming'],
            'running': ['running'],
            'yoga': ['yoga'],
            'fitness': ['fitness', 'gym', 'workout'],
            'cooking': ['cooking', 'recipe', 'food', 'chef', 'kitchen', 'baking'],
            'travel': ['travel', 'trip', 'journey', 'explore', 'adventure', 'vacation'],
            'photography': ['photography', 'photo', 'camera', 'picture', 'capture'],
            'dancing': ['dancing', 'dance', 'choreography', 'ballet', 'classical dance'],
            'gaming': ['gaming', 'game', 'video game', 'console', 'mobile game'],
            'technology': ['technology', 'tech', 'programming', 'coding', 'computer', 'software'],
            'nature': ['nature', 'environment', 'gardening', 'plants', 'outdoor', 'hiking'],
            'writing': ['writing', 'blog', 'journal', 'story', 'article', 'content', 'writer', 'author', 'aspiring writer'],
            'movies': ['movies', 'cinema', 'film', 'actor', 'director', 'bollywood', 'hollywood'],
            'fashion': ['fashion', 'style', 'clothing', 'design', 'trend', 'outfit']
        }
        
        # Check for interests in the message
        for interest, keywords in interest_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                # Check if this specific interest is not already in current interests
                current_interests_lower = current_interests.lower() if current_interests else ""
                if interest not in current_interests_lower:
                    # Also check if any of the keywords are not already mentioned
                    keyword_found = any(keyword in message_lower for keyword in keywords)
                    keyword_already_exists = any(keyword in current_interests_lower for keyword in keywords)
                    
                    if keyword_found and not keyword_already_exists:
                        discovered_interests.append(interest)
                        logger.info(f"Discovered new interest: {interest} from keywords: {keywords}")
        
        # Special case for Kolkata poetry context
        if hometown and 'kolkata' in hometown.lower() and any(word in message_lower for word in ['poetry', 'poem', 'poet']):
            if 'jibanananda das' in message_lower or 'rabindranath tagore' in message_lower:
                if 'poetry' not in current_interests.lower():
                    discovered_interests.append('poetry')
        
        return ', '.join(discovered_interests) if discovered_interests else ""
    
    def _detect_disinterest(self, message: str, current_interests: str) -> str:
        """Detect if user is expressing disinterest in any current interests"""
        message_lower = message.lower()
        current_interests_lower = current_interests.lower() if current_interests else ""
        
        # Disinterest keywords
        disinterest_keywords = [
            'not interested', 'not into', 'don\'t like', 'don\'t enjoy', 
            'not my thing', 'not for me', 'hate', 'dislike', 'boring',
            'not really', 'not much', 'not a fan', 'not into it',
            'don\'t really like', 'don\'t really enjoy', 'none', 'no',
            'don\'t watch', 'don\'t play', 'don\'t read', 'don\'t listen',
            'don\'t do', 'not into', 'not into it'
        ]
        
        # Check if user is expressing general disinterest
        is_disinterest = any(keyword in message_lower for keyword in disinterest_keywords)
        logger.info(f"Disinterest check for '{message_lower}': {is_disinterest}")
        
        if not is_disinterest:
            return ""
        
        # Map specific disinterest mentions to interest categories
        disinterest_mapping = {
            'cooking': ['cooking', 'cook', 'food', 'recipe', 'kitchen', 'baking'],
            'football': ['football', 'soccer'],
            'cricket': ['cricket'],
            'reading': ['reading', 'book', 'novel', 'novels', 'literature'],
            'sports': ['sports', 'sport', 'game', 'games'],
            'music': ['music', 'song', 'singing'],
            'art': ['art', 'painting', 'drawing'],
            'travel': ['travel', 'trip', 'journey'],
            'photography': ['photography', 'photo', 'camera'],
            'dancing': ['dancing', 'dance'],
            'gaming': ['gaming', 'game', 'video game'],
            'technology': ['technology', 'tech', 'programming'],
            'nature': ['nature', 'environment', 'gardening'],
            'writing': ['writing', 'blog', 'journal'],
            'movies': ['movies', 'cinema', 'film'],
            'fashion': ['fashion', 'style', 'clothing']
        }
        
        removed_interests = []
        
        # Check each interest category for disinterest
        for interest, keywords in disinterest_mapping.items():
            if interest in current_interests_lower:
                # Special case: if user says "none" or "no" at the beginning of message
                # This means they're rejecting the previous question/topic
                if message_lower.startswith(('none', 'no')):
                    # If the interest is NOT mentioned in the message, they're rejecting it
                    interest_not_mentioned = not any(keyword in message_lower for keyword in keywords)
                    if interest_not_mentioned and interest not in removed_interests:
                        removed_interests.append(interest)
                        logger.info(f"Found disinterest in {interest} via 'none/no' response (interest not mentioned)")
                else:
                    # Check if any keyword for this interest is mentioned in disinterest context
                    for keyword in keywords:
                        if keyword in message_lower:
                            # Check if the keyword appears in a negative context
                            # Look for negative words before or after the keyword
                            keyword_pos = message_lower.find(keyword)
                            if keyword_pos != -1:
                                # Check context around the keyword
                                context_start = max(0, keyword_pos - 20)
                                context_end = min(len(message_lower), keyword_pos + len(keyword) + 20)
                                context = message_lower[context_start:context_end]
                                
                                # Check for negative context
                                negative_context_words = ['don\'t', 'not', 'hate', 'dislike', 'boring', 'not into']
                                has_negative_context = any(neg_word in context for neg_word in negative_context_words)
                                
                                if has_negative_context:
                                    removed_interests.append(interest)
                                    logger.info(f"Found disinterest in {interest} via keyword '{keyword}' with negative context")
                                    break
        
        return ', '.join(removed_interests) if removed_interests else ""
    
    def _remove_interests_from_string(self, interests_string: str, interests_to_remove: str) -> str:
        """Remove specific interests from a comma-separated string"""
        if not interests_string or not interests_to_remove:
            return interests_string
        
        # Split into list
        interests_list = [interest.strip() for interest in interests_string.split(',')]
        remove_list = [interest.strip() for interest in interests_to_remove.split(',')]
        
        # Remove interests (case-insensitive)
        filtered_interests = []
        for interest in interests_list:
            should_remove = False
            for remove_interest in remove_list:
                if interest.lower() == remove_interest.lower():
                    should_remove = True
                    break
            if not should_remove:
                filtered_interests.append(interest)
        
        return ', '.join(filtered_interests)
    
    def discover_user_interests(self, message: str, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Discover user interests from their message and update CSV (legacy method)"""
        return self.ask_trivia_and_discover_interests(message, username, user_id, language)
    
    def generate_response(self, message: str, language: str = "English", username: Optional[str] = None, user_id: Optional[int] = None) -> str:
        """Generate a personalized, compassionate response using Gemini 2.5 Flash"""
        try:
            # Get user's first name for personalization
            first_name = ""
            if username or user_id:
                from services.data_processing import CSVDataProcessor
                csv_processor = CSVDataProcessor()
                first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            
            # Create a personalized, compassionate prompt
            name_part = f"{first_name}, " if first_name else ""
            system_context = f"""You are Sahay, a compassionate and supportive wellness companion for students in India.

IMPORTANT CONSTRAINTS:
- Keep responses SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and warm in tone
- Be FRIENDLY and approachable
- Use the student's first name naturally: {name_part if first_name else ""}
- Always prioritize emotional support and encouragement

Please respond in {language}. Be warm, supportive, and culturally sensitive.

Student message: {message}

Provide a brief, encouraging response that addresses their concern. {f"Remember to use {first_name}'s name naturally in your response." if first_name else ""}"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback = f"I'm here to help you{f', {first_name}' if first_name else ''}! Please try asking me again."
            return fallback
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates for different interaction types with multi-language support"""
        return {
            "system_context": """
            You are Sahay, a compassionate and supportive wellness companion for students in India.
            Your role is to:
            1. Provide emotional support and encouragement in any language the student prefers
            2. Help with study tips and learning strategies
            3. Offer career guidance and realistic advice
            4. Detect signs of stress or anxiety and respond appropriately
            5. Maintain a warm, friendly, and non-judgmental tone
            6. Respond in the same language the student uses (English, Hindi, Bengali, or any other language)
            7. Use Google Search when appropriate to find current, relevant information
            
            Important guidelines:
            - Always prioritize student wellbeing
            - Be culturally sensitive and respectful of Indian educational context
            - Keep responses concise and actionable
            - Suggest professional help when needed
            - Never store or reference personal health information
            - Match the language and communication style of the student
            - Use Google Search to provide up-to-date information about courses, career paths, mental health resources
            """,
            
            "greeting": """
            Student Profile:
            - Interests: {interests}
            - Language Preference: {language}
            - Age Group: {age_band}
            
            Create a warm, personalized greeting that:
            1. References one of their interests naturally
            2. Sets a supportive tone
            3. Asks an open-ended question to start conversation
            4. IMPORTANT: Respond in the student's preferred language ({language})
            5. If language is Hindi, use Devanagari script
            6. If language is Bengali, use Bengali script
            7. If no specific language preference, use English
            
            Keep it brief (2-3 sentences) and friendly. Show cultural awareness.
            """,
            
            "wellness_check": """
            Student Context:
            - Current Mood Score: {mood_score}/10
            - Anxiety Level: {anxiety_score}/10
            - Recent Message: {message}
            - Language: {language}
            
            Respond with empathy and understanding. If scores indicate distress:
            1. Acknowledge their feelings
            2. Offer practical coping strategies suitable for Indian students
            3. Suggest appropriate resources or actions
            4. IMPORTANT: Respond in the same language as their message or preferred language ({language})
            5. Use Google Search if needed to find local mental health resources
            
            Keep response supportive and non-clinical. Be culturally sensitive.
            """,
            
            "study_support": """
            Student is studying: {topic}
            Difficulty Level: {difficulty}
            Current Challenge: {challenge}
            Language: {language}
            
            Provide:
            1. A specific study technique for this topic
            2. Encouragement based on their progress
            3. A micro-action they can do right now
            4. IMPORTANT: Respond in the language specified ({language})
            5. Consider Indian educational context and examination systems
            6. Use Google Search to find current online resources, tutorials, or study materials
            
            Make it practical and immediately actionable.
            """,
            
            "career_guidance": """
            Student Profile:
            - Interests: {interests}
            - Current Field: {current_field}
            - Exploring: {explore_field}
            - Language: {language}
            
            Provide balanced career advice that:
            1. Acknowledges both paths (current and exploratory)
            2. Gives realistic pros and cons considering Indian job market
            3. Suggests concrete next steps
            4. Avoids over-promising or creating unrealistic expectations
            5. IMPORTANT: Respond in the language specified ({language})
            6. Use Google Search to find current job market trends, salary information, and skill requirements
            
            Be honest about challenges while remaining encouraging. Consider Indian industry context.
            """,
            
            "crisis_response": """
            IMPORTANT: Student shows signs of high distress.
            Risk Level: {risk_level}
            Language: {language}
            
            Response must:
            1. Show immediate care and concern
            2. Provide crisis resources suitable for India
            3. Encourage professional support
            4. Offer immediate coping techniques
            5. Never minimize their feelings
            6. IMPORTANT: Respond in the language specified ({language})
            7. Use Google Search to find local helplines and mental health services
            
            Priority is safety and support.
            """,
            
            "action_generation": """
            Based on student's current state:
            - Wellness Level: {wellness_level}
            - Energy Level: {energy_level}
            - Available Time: {time_available} minutes
            - Interests: {interests}
            - Language: {language}
            
            Generate 3 personalized micro-actions that are:
            1. Achievable in their current state
            2. Aligned with their interests
            3. Supportive of their wellbeing
            4. Culturally appropriate for Indian students
            5. Use Google Search if needed to find specific resources or activities
            
            IMPORTANT: If language is not English, provide action descriptions in {language}
            
            Format as JSON:
            [
                {{"action": "...", "duration": X, "category": "..."}},
                ...
            ]
            """,
            
            "multi_language_chat": """
            Previous conversation context: {context}
            Student's message: {message}
            Detected/Preferred Language: {language}
            
            Instructions:
            1. Respond naturally in the same language as the student's message
            2. If the student switches languages, switch with them
            3. Maintain the supportive Sahay personality across all languages
            4. Use Google Search when the student asks for current information, resources, or links
            5. Be culturally appropriate for the language and region
            6. If asked for resources, provide relevant links and information
            
            Respond as Sahay would, maintaining warmth and support.
            """
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text using simple heuristics"""
        # Simple language detection based on script and common words
        import re
        
        # Check for Devanagari script (Hindi)
        if re.search(r'[\u0900-\u097F]', text):
            return "Hindi"
        
        # Check for Bengali script
        if re.search(r'[\u0980-\u09FF]', text):
            return "Bengali"
        
        # Check for common Hindi words in Roman script
        hindi_words = ['hai', 'mein', 'aur', 'ke', 'ki', 'ka', 'kya', 'kaise', 'kab', 'kahan', 'nahin', 'haan']
        text_lower = text.lower()
        if any(word in text_lower for word in hindi_words):
            return "Hindi"
        
        # Default to English
        return "English"
    
    def _generate_content_with_language(self, message: str, language: str = "English", enable_search: bool = False) -> str:
        """Generate content with language support and optional Google Search"""
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=message)]
                )
            ]
            
            # Use configuration with or without search
            if enable_search:
                config = self.generation_config  # Has Google Search enabled
            else:
                # Create config without search for simple interactions
                config = types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.9,
                    seed=42,
                    max_output_tokens=2048,
                    safety_settings=self.generation_config.safety_settings,
                    thinking_config=self.generation_config.thinking_config,
                )
            
            response_text = ""
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=message,  # Pass the string directly
                config=config,
            ):
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                    if chunk.text:
                        response_text += chunk.text
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return ""
    
    def _get_chat_history(self, student_id: str) -> List[Dict]:
        """Get chat history for a student (simplified for CSV system)"""
        if student_id not in self.chat_histories:
            # Initialize with system context
            self.chat_histories[student_id] = []
        return self.chat_histories[student_id]

    def _add_to_chat_history(self, student_id: str, user_message: str, assistant_response: str):
        """Add interaction to chat history"""
        history = self._get_chat_history(student_id)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_response})
    
    def generate_greeting(self, student_profile: Dict[str, Any]) -> str:
        """Generate personalized greeting for a student in their preferred language"""
        try:
            language = student_profile.get("language_pref", "English")
            
            prompt = self.prompts["greeting"].format(
                interests=", ".join(student_profile.get("interests", ["learning"])),
                language=language,
                age_band=student_profile.get("age_band", "18-22")
            )
            
            response = self._generate_content_with_language(prompt, language)
            return response if response else "Hello! I'm Sahay, your wellness companion. How are you feeling today?"
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return "Hello! I'm Sahay, your wellness companion. How are you feeling today?"
    
    def process_chat_message(
        self,
        student_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        enable_search: bool = False
    ) -> Dict[str, Any]:
        """Process a chat message from a student with language detection and optional search"""
        try:
            # Detect language from the message
            detected_language = self._detect_language(message)
            
            # Get preferred language from context or use detected
            preferred_language = detected_language
            if context and context.get("language_pref"):
                preferred_language = context["language_pref"]
            
            # Get chat history
            history = self._get_chat_history(student_id)
            
            # Add context to message if provided
            enhanced_message = message
            if context:
                context_info = []
                if context.get("mood_score"):
                    context_info.append(f"Mood: {context['mood_score']}/10")
                if context.get("anxiety_score"):
                    context_info.append(f"Anxiety: {context['anxiety_score']}/10")
                if context_info:
                    enhanced_message = f"[Context: {', '.join(context_info)}] Student says: {message}"
            
            # Use multi-language chat prompt
            chat_prompt = self.prompts["multi_language_chat"].format(
                context=self._build_conversation_context(history),
                message=enhanced_message,
                language=preferred_language
            )
            
            # Enable search if needed (when student asks for resources, links, current info)
            search_keywords = ["link", "resource", "website", "search", "find", "latest", "current", "news", "course", "job"]
            should_use_search = enable_search or any(keyword in message.lower() for keyword in search_keywords)
            
            # Generate response
            response = self._generate_content_with_language(chat_prompt, preferred_language, should_use_search)
            
            if response:
                # Add to history
                self._add_to_chat_history(student_id, message, response)
                
                # Analyze response for risk indicators
                risk_analysis = self._analyze_risk_indicators(message, response)
                
                return {
                    "response": response,
                    "timestamp": timezone.now().isoformat(),
                    "language": preferred_language,
                    "search_enabled": should_use_search,
                    "risk_indicators": risk_analysis,
                    "suggested_actions": self._generate_suggested_actions(risk_analysis)
                }
            else:
                fallback_message = self._get_fallback_message(preferred_language)
                return {
                    "response": fallback_message,
                    "timestamp": timezone.now().isoformat(),
                    "language": preferred_language
                }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            fallback_message = self._get_fallback_message("English")
            return {
                "response": fallback_message,
                "error": str(e)
            }
    
    def _build_conversation_context(self, history: List[Dict]) -> str:
        """Build conversation context from history"""
        context = ""
        for content in history[-4:]:  # Last 2 exchanges
            role = "Student" if content["role"] == "user" else "Sahay"
            text = content.get("content", "")
            context += f"{role}: {text}\n"
        return context
    
    def _get_fallback_message(self, language: str, first_name: str = "") -> str:
        """Get fallback message in appropriate language with personalization"""
        name_part = f"{first_name}, " if first_name else ""
        fallbacks = {
            "Hindi": f"{name_part}मैं यहाँ आपकी बात सुनने के लिए हूँ। कृपया बताएं कि आप कैसा महसूस कर रहे हैं?",
            "Bengali": f"{name_part}আমি এখানে আপনার কথা শুনতে আছি। আপনি কেমন অনুভব করছেন তা বলুন।",
            "English": f"{name_part}I'm here to listen. Could you tell me more about how you're feeling?"
        }
        return fallbacks.get(language, fallbacks["English"])
    
    def generate_wellness_response(
        self,
        mood_score: int,
        anxiety_score: int,
        message: str = "",
        language: str = "English",
        username: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> str:
        """Generate personalized wellness response based on scores in specified language"""
        first_name = ""
        try:
            # Get user's first name for personalization
            if username or user_id:
                from services.data_processing import CSVDataProcessor
                csv_processor = CSVDataProcessor()
                first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            
            # Auto-detect language if not provided
            if message and language == "English":
                language = self._detect_language(message)
            
            # Create personalized wellness prompt
            name_part = f"{first_name}, " if first_name else ""
            prompt = f"""You are Sahay, a compassionate wellness companion for students.

IMPORTANT CONSTRAINTS:
- Keep response SHORT (2-3 sentences maximum)
- Be COMPASSIONATE and understanding
- Be FRIENDLY and warm
- Use the student's first name: {name_part if first_name else ""}

Student Context:
- Current Mood Score: {mood_score}/10
- Anxiety Level: {anxiety_score}/10
- Recent Message: {message}
- Language: {language}

{f"{first_name}, respond" if first_name else "Respond"} with empathy and understanding in {language}. Acknowledge their feelings and offer one practical coping strategy."""
            
            # Enable search for mental health resources
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            return response if response else self._get_fallback_message(language, first_name)
            
        except Exception as e:
            logger.error(f"Error generating wellness response: {e}")
            return self._get_fallback_message(language, first_name)
    
    def generate_study_tips(
        self,
        topic: str,
        difficulty: str,
        challenge: str,
        language: str = "English"
    ) -> str:
        """Generate personalized study tips in specified language"""
        try:
            prompt = self.prompts["study_support"].format(
                topic=topic,
                difficulty=difficulty,
                challenge=challenge,
                language=language
            )
            
            # Enable search for study resources and tutorials
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            return response if response else "Try breaking down the topic into smaller parts. Focus on understanding one concept at a time."
            
        except Exception as e:
            logger.error(f"Error generating study tips: {e}")
            return "Try breaking down the topic into smaller parts. Focus on understanding one concept at a time."
    
    def generate_career_advice(
        self,
        interests: List[str],
        current_field: str,
        explore_field: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate career guidance with dual-track approach in specified language"""
        try:
            prompt = self.prompts["career_guidance"].format(
                interests=", ".join(interests),
                current_field=current_field,
                explore_field=explore_field,
                language=language
            )
            
            # Enable search for job market trends and salary information
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            
            if response:
                # Parse response to extract structured advice
                advice = {
                    "summary": response,
                    "current_track": self._extract_track_advice(response, current_field),
                    "explore_track": self._extract_track_advice(response, explore_field),
                    "next_steps": self._extract_next_steps(response),
                    "calibration": self._generate_calibration_metrics(current_field, explore_field),
                    "language": language
                }
                return advice
            else:
                return {
                    "summary": "Both paths have potential. Focus on building transferable skills.",
                    "current_track": "Build foundational skills",
                    "explore_track": "Research requirements",
                    "next_steps": ["Identify core skills", "Find mentors", "Start learning"],
                    "calibration": self._generate_calibration_metrics(current_field, explore_field),
                    "language": language
                }
            
        except Exception as e:
            logger.error(f"Error generating career advice: {e}")
            return {
                "summary": "Both paths have potential. Focus on building transferable skills.",
                "language": language,
                "error": str(e)
            }
    
    def generate_personalized_actions(
        self,
        wellness_level: str,
        energy_level: int,
        time_available: int,
        interests: List[str],
        language: str = "English"
    ) -> List[Dict[str, Any]]:
        """Generate personalized micro-actions in specified language"""
        try:
            prompt = self.prompts["action_generation"].format(
                wellness_level=wellness_level,
                energy_level=energy_level,
                time_available=time_available,
                interests=", ".join(interests),
                language=language
            )
            
            # Enable search for finding specific activities and resources
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            
            # Try to parse JSON response
            if response:
                try:
                    actions = json.loads(response)
                    return actions
                except json.JSONDecodeError:
                    # Fallback to default actions
                    return self._get_default_actions(wellness_level, interests, language)
            else:
                return self._get_default_actions(wellness_level, interests, language)
                
        except Exception as e:
            logger.error(f"Error generating actions: {e}")
            return self._get_default_actions(wellness_level, interests, language)
    
    def handle_crisis_situation(
        self,
        student_id: str,
        risk_level: str,
        context: Dict[str, Any],
        language: str = "English"
    ) -> Dict[str, Any]:
        """Handle high-risk situations with appropriate response in specified language"""
        try:
            prompt = self.prompts["crisis_response"].format(
                risk_level=risk_level,
                language=language
            )
            
            # Enable search for local mental health resources and helplines
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            
            # Log crisis interaction (anonymized)
            self._log_crisis_interaction(student_id, risk_level)
            
            return {
                "response": response if response else self._get_crisis_fallback(language),
                "resources": self._get_crisis_resources(language),
                "escalation_needed": risk_level == "L3",
                "follow_up_required": True,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Error handling crisis: {e}")
            return {
                "response": self._get_crisis_fallback(language),
                "resources": self._get_crisis_resources(language),
                "escalation_needed": True,
                "language": language
            }
    
    def _get_crisis_fallback(self, language: str) -> str:
        """Get crisis fallback message in appropriate language"""
        fallbacks = {
            "Hindi": "मुझे आपकी बहुत चिंता है। कृपया किसी काउंसलर या विश्वसनीय व्यक्ति से बात करें।",
            "Bengali": "আমি আপনার জন্য খুবই চিন্তিত। অনুগ্রহ করে একজন কাউন্সেলর বা বিশ্বস্ত কারো সাথে কথা বলুন।",
            "English": "I'm really concerned about you. Please reach out to a counselor or trusted adult."
        }
        return fallbacks.get(language, fallbacks["English"])
    
    def _analyze_risk_indicators(self, message: str, response: str) -> Dict[str, Any]:
        """Analyze messages for risk indicators"""
        risk_keywords = {
            "high": ["suicide", "kill myself", "end it all", "can't go on", "hopeless"],
            "medium": ["depressed", "anxious", "stressed", "overwhelmed", "can't cope"],
            "low": ["tired", "worried", "nervous", "uncertain", "confused"]
        }
        
        message_lower = message.lower()
        detected_level = "none"
        detected_keywords = []
        
        for level, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    detected_keywords.append(keyword)
                    if level == "high" or (level == "medium" and detected_level != "high"):
                        detected_level = level
                    elif level == "low" and detected_level == "none":
                        detected_level = level
        
        return {
            "level": detected_level,
            "keywords": detected_keywords,
            "timestamp": timezone.now().isoformat()
        }
    
    def _generate_suggested_actions(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate suggested actions based on risk analysis"""
        level = risk_analysis.get("level", "none")
        
        actions = {
            "high": [
                "Immediate counselor referral",
                "Crisis hotline information",
                "Emergency contact notification"
            ],
            "medium": [
                "Schedule wellness check-in",
                "Provide coping resources",
                "Suggest peer support group"
            ],
            "low": [
                "Offer relaxation techniques",
                "Suggest self-care activities",
                "Schedule follow-up in 24 hours"
            ],
            "none": [
                "Continue regular support",
                "Provide study resources",
                "Maintain positive engagement"
            ]
        }
        
        return actions.get(level, actions["none"])
    
    def _extract_track_advice(self, text: str, field: str) -> str:
        """Extract advice specific to a career track"""
        # Simple extraction - in production, use NLP
        lines = text.split('\n')
        relevant_lines = [line for line in lines if field.lower() in line.lower()]
        return ' '.join(relevant_lines[:2]) if relevant_lines else "Build foundational skills"
    
    def _extract_next_steps(self, text: str) -> List[str]:
        """Extract actionable next steps from career advice"""
        # Simple extraction - look for numbered items or action verbs
        action_verbs = ["learn", "practice", "build", "create", "join", "complete", "study"]
        lines = text.split('\n')
        steps = []
        
        for line in lines:
            if any(verb in line.lower() for verb in action_verbs):
                steps.append(line.strip())
        
        return steps[:3]  # Return top 3 steps
    
    def _generate_calibration_metrics(self, current_field: str, explore_field: str) -> Dict[str, int]:
        """Generate realistic calibration metrics for career paths"""
        # Simplified scoring - in production, use data-driven approach
        return {
            "current_confidence": 75,
            "explore_feasibility": 60,
            "time_investment": 6,  # months
            "skill_gap": 30  # percentage
        }
    
    def _get_default_actions(self, wellness_level: str, interests: List[str], language: str = "English") -> List[Dict[str, Any]]:
        """Get default actions when generation fails - now with language support"""
        # Language-specific action categories
        action_categories = {
            "English": {
                "study": "focused study session",
                "explore": "Explore",
                "connect": "Connect with a study buddy",
                "breathing": "breathing exercise",
                "walk": "Take a short walk",
                "review": "Review notes briefly",
                "music": "Listen to calming music",
                "journal": "Write in a journal",
                "rest": "Rest and hydrate"
            },
            "Hindi": {
                "study": "केंद्रित अध्ययन सत्र",
                "explore": "अन्वेषण करें",
                "connect": "अध्ययन मित्र से जुड़ें",
                "breathing": "श्वसन अभ्यास",
                "walk": "छोटी सैर करें",
                "review": "नोट्स की समीक्षा करें",
                "music": "शांत संगीत सुनें",
                "journal": "डायरी में लिखें",
                "rest": "आराम करें और पानी पिएं"
            },
            "Bengali": {
                "study": "মনোযোগী অধ্যয়ন সেশন",
                "explore": "অন্বেষণ করুন",
                "connect": "অধ্যয়ন বন্ধুর সাথে যোগাযোগ করুন",
                "breathing": "শ্বাসের ব্যায়াম",
                "walk": "ছোট হাঁটাহাঁটি করুন",
                "review": "নোট সংক্ষেপে পর্যালোচনা করুন",
                "music": "শান্ত সংগীত শুনুন",
                "journal": "জার্নালে লিখুন",
                "rest": "বিশ্রাম নিন এবং পানি পান করুন"
            }
        }
        
        categories = action_categories.get(language, action_categories["English"])
        
        actions = {
            "high_wellness": [
                {"action": f"15-minute {categories['study']}", "duration": 15, "category": "study"},
                {"action": f"{categories['explore']} {interests[0] if interests else 'a hobby'}", "duration": 20, "category": "interest"},
                {"action": categories["connect"], "duration": 30, "category": "social"}
            ],
            "medium_wellness": [
                {"action": f"5-minute {categories['breathing']}", "duration": 5, "category": "wellness"},
                {"action": categories["walk"], "duration": 10, "category": "wellness"},
                {"action": categories["review"], "duration": 10, "category": "study"}
            ],
            "low_wellness": [
                {"action": categories["music"], "duration": 5, "category": "wellness"},
                {"action": categories["journal"], "duration": 10, "category": "wellness"},
                {"action": categories["rest"], "duration": 15, "category": "self-care"}
            ]
        }
        
        return actions.get(f"{wellness_level}_wellness", actions["medium_wellness"])
    
    def _get_crisis_resources(self, language: str = "English") -> Dict[str, Any]:
        """Get crisis resources based on location and language"""
        # Base resources (numbers are international)
        base_resources = {
            "hotlines": [
                {"name": "National Suicide Prevention Lifeline", "number": "988"},
                {"name": "Crisis Text Line", "number": "Text HOME to 741741"},
                {"name": "SAMHSA National Helpline", "number": "1-800-662-4357"}
            ],
            "online_resources": [
                "https://www.crisistextline.org/",
                "https://suicidepreventionlifeline.org/",
                "https://www.samhsa.gov/find-help"
            ],
            "campus_resources": [
                "Student Counseling Center",
                "Campus Health Services", 
                "Peer Support Groups"
            ]
        }
        
        # Add language-specific resources
        if language == "Hindi":
            base_resources["local_resources"] = [
                "भारतीय मानसिक स्वास्थ्य हेल्पलाइन: +91-9152987821",
                "वंदरेवाला फाउंडेशन: +91-9999666555"
            ]
        elif language == "Bengali":
            base_resources["local_resources"] = [
                "বাংলাদেশ মানসিক স্বাস্থ্য হেল্পলাইন: ০৯৬১১৬৭৭৭৭৭",
                "কাটো আশা: ০১৭৭৯৫৫৪৪৪৪"
            ]
        
        return base_resources
    
    def _log_crisis_interaction(self, student_id: str, risk_level: str):
        """Log crisis interaction (anonymized)"""
        # Hash student ID for privacy
        hashed_id = hashlib.sha256(student_id.encode()).hexdigest()[:8]
        
        logger.warning(f"Crisis interaction logged: {hashed_id} - Level: {risk_level}")
        
        # In production, this would trigger appropriate alerts
        # while maintaining student privacy
    
    def clear_session(self, student_id: str):
        """Clear chat session for a student"""
        if student_id in self.chat_histories:
            del self.chat_histories[student_id]
            logger.info(f"Cleared chat session for student: {student_id[:4]}***")


class PromptOptimizer:
    """Optimize prompts for better responses"""
    
    def __init__(self):
        self.performance_metrics = {}
    
    def optimize_prompt(self, prompt_type: str, original_prompt: str) -> str:
        """Optimize prompt based on performance metrics"""
        # Add clarity improvements
        optimizations = {
            "greeting": self._add_greeting_context,
            "wellness_check": self._add_wellness_context,
            "study_support": self._add_study_context,
            "career_guidance": self._add_career_context
        }
        
        optimizer = optimizations.get(prompt_type, lambda x: x)
        return optimizer(original_prompt)
    
    def _add_greeting_context(self, prompt: str) -> str:
        """Add context for better greetings"""
        return f"""
        {prompt}
        
        Additional context:
        - Time of day: {timezone.now().strftime('%H:%M')}
        - Day of week: {timezone.now().strftime('%A')}
        
        Adjust greeting accordingly (morning/afternoon/evening).
        """
    
    def _add_wellness_context(self, prompt: str) -> str:
        """Add context for wellness responses"""
        return f"""
        {prompt}
        
        Important: 
        - Validate feelings without being dismissive
        - Offer specific, actionable coping strategies
        - Suggest resources appropriate to the risk level
        """
    
    def _add_study_context(self, prompt: str) -> str:
        """Add context for study support"""
        return f"""
        {prompt}
        
        Consider:
        - Learning style (visual/auditory/kinesthetic)
        - Time management techniques
        - Subject-specific strategies
        """
    
    def _add_career_context(self, prompt: str) -> str:
        """Add context for career guidance"""
        return f"""
        {prompt}
        
        Include:
        - Industry trends and job market reality
        - Skill development timeline
        - Alternative pathways
        - Networking opportunities
        """
    
    def mental_wellbeing(self, message: str, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Provide mental wellbeing support using hometown and interests for personalized examples"""
        try:
            from services.data_processing import CSVDataProcessor
            csv_processor = CSVDataProcessor()
            
            # Get user information
            first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            hometown = csv_processor.get_user_hometown(username=username, user_id=user_id)
            course = csv_processor.get_user_course(username=username, user_id=user_id)
            interests = csv_processor.get_user_interests(username=username, user_id=user_id)
            
            system_context = f"""You are Sahay, a compassionate mental wellness companion. Help the user with their mental health concerns using personalized examples from their hometown and interests.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's hometown: {hometown if hometown else "Not provided"}
- User's course: {course if course else "Not provided"}
- User's interests: {interests if interests else "Not provided"}
- User's message: {message}
- Response language: {language}

APPROACH:
- Be empathetic and understanding
- Use storytelling and examples from their hometown
- Connect solutions to their interests for relatability
- Provide practical, actionable advice
- Use metaphors and analogies they can relate to

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- ALWAYS end with an engaging question - THIS IS MANDATORY
- Use examples from their hometown when possible
- Connect advice to their interests
- Be warm and supportive
- Respond in {language}
- NEVER end with a statement - ALWAYS end with a question mark

HOMETOWN EXAMPLES:
- Kolkata: Use examples like "walking along the Hooghly riverbank", "visiting Victoria Memorial", "enjoying street food in Park Street"
- Mumbai: Use examples like "strolling on Marine Drive", "watching sunset at Gateway of India", "enjoying vada pav"
- Delhi: Use examples like "walking in Lodhi Gardens", "visiting India Gate", "enjoying street food in Chandni Chowk"

INTEREST CONNECTIONS:
- Football: Use team spirit, teamwork, persistence metaphors
- Reading: Use book characters, story arcs, narrative metaphors
- Movies: Use film plots, character development, cinematic metaphors
- Writing: Use creative expression, storytelling, narrative metaphors
- Science Fiction: Use futuristic thinking, innovation, imagination metaphors

CRITICAL: Your response MUST end with a question mark (?). No exceptions.

EXAMPLES OF GOOD RESPONSES:
- "I understand you're feeling overwhelmed, Koushik. Just like how East Bengal fans never give up during tough matches, you too can find your inner strength. What's one small thing that usually helps you feel calmer?"
- "Feeling stressed is like being in a complex sci-fi plot - overwhelming at first, but with the right approach, you can navigate through it. What's your favorite way to unwind when things feel too much?"

Provide mental wellness support with personalized examples:"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            response_text = response.text.strip()
            
            # Ensure response ends with a question
            if not response_text.endswith('?'):
                response_text += " What's one thing that usually helps you feel better?"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in mental wellbeing support: {e}")
            return f"I'm here to support you, {first_name if first_name else 'friend'}. Let's work through this together. What's one small thing that usually helps you feel better?"
    
    def study_guide(self, message: str, username: Optional[str] = None, user_id: Optional[int] = None, language: str = "English") -> str:
        """Provide study guidance using hometown and interests for personalized examples"""
        try:
            from services.data_processing import CSVDataProcessor
            csv_processor = CSVDataProcessor()
            
            # Get user information
            first_name = csv_processor.get_user_first_name(username=username, user_id=user_id)
            hometown = csv_processor.get_user_hometown(username=username, user_id=user_id)
            course = csv_processor.get_user_course(username=username, user_id=user_id)
            interests = csv_processor.get_user_interests(username=username, user_id=user_id)
            
            system_context = f"""You are Sahay, a supportive study companion. Help the user with their academic challenges using personalized examples from their hometown and interests.

CONTEXT:
- User's name: {first_name if first_name else "Not provided"}
- User's hometown: {hometown if hometown else "Not provided"}
- User's course: {course if course else "Not provided"}
- User's interests: {interests if interests else "Not provided"}
- User's message: {message}
- Response language: {language}

APPROACH:
- Provide practical study techniques
- Use examples from their hometown for relatability
- Connect study methods to their interests
- Make learning feel engaging and relevant
- Give specific, actionable advice

REQUIREMENTS:
- Keep response SHORT (2-3 sentences maximum)
- ALWAYS end with an engaging question - THIS IS MANDATORY
- Use examples from their hometown when possible
- Connect study methods to their interests
- Be encouraging and supportive
- Respond in {language}
- NEVER end with a statement - ALWAYS end with a question mark

HOMETOWN STUDY EXAMPLES:
- Kolkata: Use examples like "studying at Coffee House", "group study at Maidan", "quiet corners in College Street"
- Mumbai: Use examples like "studying at Marine Drive", "library sessions at Asiatic Society", "study groups at Gateway"
- Delhi: Use examples like "studying at India Gate lawns", "library time at CP", "study sessions at Lodhi Gardens"

INTEREST-BASED STUDY METHODS:
- Football: Use team strategies, game plans, practice routines
- Reading: Use story structures, character analysis, narrative techniques
- Movies: Use scene analysis, plot structures, visual learning
- Writing: Use creative techniques, storytelling methods, expression
- Science Fiction: Use futuristic thinking, innovation, imagination

CRITICAL: Your response MUST end with a question mark (?). No exceptions.

EXAMPLES OF GOOD RESPONSES:
- "I hear you, Koushik! Studying can feel overwhelming, just like preparing for a big football match. Try breaking your studies into smaller sessions, like training drills. What subject are you finding most challenging right now?"
- "Think of studying like reading a complex sci-fi novel - start with the basics and build your understanding chapter by chapter. What's your preferred learning style when tackling difficult concepts?"

Provide study guidance with personalized examples:"""
            
            response = self.model.generate_content(
                system_context,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            response_text = response.text.strip()
            
            # Ensure response ends with a question
            if not response_text.endswith('?'):
                response_text += " What's one subject you'd like to focus on improving?"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in study guide support: {e}")
            return f"I'm here to help with your studies, {first_name if first_name else 'friend'}. Let's find a method that works for you. What subject are you finding most challenging right now?"
 
 