"""
services/gemini_service.py - Gemini AI Integration for Sahay (Updated for CSV-based system)
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service class for interacting with Google's Gemini AI model using the new GenAI SDK
    """
    
    def __init__(self, project_id: str = "pro-router-459418-t0", location: str = "global"):
        """Initialize Gemini client with new SDK"""
        try:
            # Initialize the GenAI client with Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
            )
            
            # Model configuration
            self.model_name = "gemini-2.5-flash"
            
            # Google Search tool for grounding
            self.search_tool = types.Tool(google_search=types.GoogleSearch())
            
            # Generation configuration with safety settings off for demo and Google Search enabled
            self.generation_config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                seed=42,  # For reproducible outputs in demo
                max_output_tokens=2048,
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE
                    )
                ],
                tools=[self.search_tool],  # Enable Google Search
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                ),
            )
            
            # Store active chat histories (simplified for CSV-based system)
            self.chat_histories = {}
            
            # Load prompt templates
            self.prompts = self._load_prompts()
            
            logger.info("Gemini service initialized successfully with new GenAI SDK")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise
    
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
    
    def _get_chat_history(self, student_id: str) -> List[types.Content]:
        """Get chat history for a student (simplified for CSV system)"""
        if student_id not in self.chat_histories:
            # Initialize with system context
            self.chat_histories[student_id] = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=self.prompts["system_context"])]
                ),
                types.Content(
                    role="model", 
                    parts=[types.Part(text="I understand. I'm Sahay, here to support students with warmth and compassion.")]
                )
            ]
        return self.chat_histories[student_id]
    
    def _add_to_chat_history(self, student_id: str, user_message: str, assistant_response: str):
        """Add interaction to chat history"""
        history = self._get_chat_history(student_id)
        history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
        history.append(types.Content(role="model", parts=[types.Part(text=assistant_response)]))
    
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
                    "timestamp": datetime.now().isoformat(),
                    "language": preferred_language,
                    "search_enabled": should_use_search,
                    "risk_indicators": risk_analysis,
                    "suggested_actions": self._generate_suggested_actions(risk_analysis)
                }
            else:
                fallback_message = self._get_fallback_message(preferred_language)
                return {
                    "response": fallback_message,
                    "timestamp": datetime.now().isoformat(),
                    "language": preferred_language
                }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            fallback_message = self._get_fallback_message("English")
            return {
                "response": fallback_message,
                "error": str(e)
            }
    
    def _build_conversation_context(self, history: List[types.Content]) -> str:
        """Build conversation context from history"""
        context = ""
        for content in history[-4:]:  # Last 2 exchanges
            role = "Student" if content.role == "user" else "Sahay"
            text = content.parts[0].text if content.parts else ""
            context += f"{role}: {text}\n"
        return context
    
    def _get_fallback_message(self, language: str) -> str:
        """Get fallback message in appropriate language"""
        fallbacks = {
            "Hindi": "मैं यहाँ आपकी बात सुनने के लिए हूँ। कृपया बताएं कि आप कैसा महसूस कर रहे हैं?",
            "Bengali": "আমি এখানে আপনার কথা শুনতে আছি। আপনি কেমন অনুভব করছেন তা বলুন।",
            "English": "I'm here to listen. Could you tell me more about how you're feeling?"
        }
        return fallbacks.get(language, fallbacks["English"])
    
    def generate_wellness_response(
        self,
        mood_score: int,
        anxiety_score: int,
        message: str = "",
        language: str = "English"
    ) -> str:
        """Generate response based on wellness scores in specified language"""
        try:
            # Auto-detect language if not provided
            if message and language == "English":
                language = self._detect_language(message)
            
            prompt = self.prompts["wellness_check"].format(
                mood_score=mood_score,
                anxiety_score=anxiety_score,
                message=message,
                language=language
            )
            
            # Enable search for mental health resources
            response = self._generate_content_with_language(prompt, language, enable_search=True)
            return response if response else self._get_fallback_message(language)
            
        except Exception as e:
            logger.error(f"Error generating wellness response: {e}")
            return self._get_fallback_message(language)
    
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
            "timestamp": datetime.now().isoformat()
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
        - Time of day: {datetime.now().strftime('%H:%M')}
        - Day of week: {datetime.now().strftime('%A')}
        
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