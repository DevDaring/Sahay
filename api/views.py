from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from services.data_processing import CSVDataProcessor
from services.gemini_service import GeminiService
import json
import uuid
from datetime import datetime, timedelta


class StudentViewSet(View):
    """Student API endpoints"""
    
    def get(self, request, student_id=None):
        """Get student data"""
        processor = CSVDataProcessor()
        students_df = processor.get_students()
        
        if student_id:
            student_data = students_df[students_df['student_id'] == student_id]
            if not student_data.empty:
                return JsonResponse(student_data.iloc[0].to_dict())
            else:
                return JsonResponse({'error': 'Student not found'}, status=404)
        else:
            return JsonResponse({
                'students': students_df.to_dict('records'),
                'count': len(students_df)
            })


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """Chat endpoint for Gemini integration"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id', 'demo_user')
            message = data.get('message', '').strip()
            language = data.get('language', 'English')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)

            # Get user information for personalization
            username = None
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                username = request.user.username
                if hasattr(request.user, 'id'):
                    user_id = request.user.id
                print(f"Live chat user: {username}, user_id: {user_id}")
            else:
                print("Live chat user not authenticated")
            
            # Initialize Gemini service
            gemini_service = GeminiService()
            
            # Use trivia and interest discovery for all messages
            response = gemini_service.ask_trivia_and_discover_interests(
                message=message,
                username=username,
                user_id=user_id,
                language=language
            )
            
            # If no response generated, use regular response as fallback
            if not response or "I'm here to listen and learn about you!" in response:
                response = gemini_service.generate_response(
                    message=message,
                    language=language,
                    username=username,
                    user_id=user_id
                )
            
            if not response or response.strip() == "":
                response = "I'm here to help! However, I'm having trouble processing your message right now. Please try again."
            
            return JsonResponse({
                'response': response,
                'session_id': f"CHAT_{uuid.uuid4().hex[:8]}",
                'timestamp': timezone.now().isoformat(),
                'detected_language': language
            })
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Chat API error: {str(e)}", exc_info=True)
            
            return JsonResponse({'error': f'Error processing message: {str(e)}'}, status=500)
    
    def _generate_demo_response(self, message, language):
        """Generate demo responses for different languages"""
        responses = {
            'English': {
                'study': "I understand you're looking for study help. Here are some effective techniques: 1) Use active recall - test yourself frequently, 2) Practice spaced repetition, 3) Break complex topics into smaller chunks. What specific subject are you working on?",
                'stress': "It sounds like you're feeling overwhelmed. That's completely normal for students. Try taking a few deep breaths. Consider breaking your tasks into smaller, manageable steps. Would you like me to suggest some quick stress-relief exercises?",
                'career': "Career planning can feel overwhelming, but you're being proactive by thinking about it! Consider exploring both your current interests and new fields. What subjects or activities do you enjoy most?",
                'default': "I'm here to help you with your studies and wellbeing. Feel free to share what's on your mind - whether it's academic challenges, stress, or career questions."
            },
            'Hindi': {
                'study': "मैं समझ सकता हूं कि आप अध्ययन में सहायता चाहते हैं। यहां कुछ प्रभावी तकनीकें हैं: 1) सक्रिय स्मरण का उपयोग करें, 2) दोहराव का अभ्यास करें, 3) जटिल विषयों को छोटे भागों में बांटें। आप किस विषय पर काम कर रहे हैं?",
                'stress': "लगता है आप परेशान हैं। यह छात्रों के लिए बिल्कुल सामान्य है। कुछ गहरी सांसें लेने की कोशिश करें। अपने कार्यों को छोटे, प्रबंधनीय चरणों में बांटने पर विचार करें। क्या आप चाहेंगे कि मैं कुछ त्वरित तनाव-राहत अभ्यास सुझाऊं?",
                'career': "करियर की योजना बनाना कठिन लग सकता है, लेकिन आप इसके बारे में सोचकर सक्रिय हो रहे हैं! अपनी वर्तमान रुचियों और नए क्षेत्रों दोनों को देखने पर विचार करें। आप किन विषयों या गतिविधियों का सबसे अधिक आनंद लेते हैं?",
                'default': "मैं आपकी पढ़ाई और कल्याण में मदद के लिए यहां हूं। जो भी आपके मन में है उसे साझा करने में संकोच न करें - चाहे वह शैक्षणिक चुनौतियां हों, तनाव हो, या करियर के सवाल हों।"
            },
            'Bengali': {
                'study': "আমি বুঝতে পারছি আপনি পড়াশোনার সাহায্য খুঁজছেন। এখানে কিছু কার্যকর কৌশল আছে: ১) সক্রিয় স্মরণ ব্যবহার করুন - নিজেকে ঘন ঘন পরীক্ষা করুন, ২) ব্যবধানে পুনরাবৃত্তি করুন, ৩) জটিল বিষয়গুলোকে ছোট অংশে ভাগ করুন। আপনি কোন নির্দিষ্ট বিষয়ে কাজ করছেন?",
                'stress': "মনে হচ্ছে আপনি অভিভূত বোধ করছেন। এটা ছাত্রদের জন্য সম্পূর্ণ স্বাভাবিক। কয়েকটি গভীর শ্বাস নেওয়ার চেষ্টা করুন। আপনার কাজগুলোকে ছোট, পরিচালনাযোগ্য ধাপে ভাগ করার কথা ভাবুন। আমি কি কিছু দ্রুত চাপ-মুক্তির ব্যায়াম সুপারিশ করব?",
                'career': "ক্যারিয়ার পরিকল্পনা কঠিন মনে হতে পারে, কিন্তু আপনি এটা নিয়ে ভেবে সক্রিয় হচ্ছেন! আপনার বর্তমান আগ্রহ এবং নতুন ক্ষেত্র উভয়ই অন্বেষণ করার কথা ভাবুন। আপনি কোন বিষয় বা কার্যকলাপ সবচেয়ে উপভোগ করেন?",
                'default': "আমি আপনার পড়াশোনা এবং কল্যাণে সাহায্য করার জন্য এখানে আছি। আপনার মনে যা আছে তা শেয়ার করতে দ্বিধা করবেন না - তা শিক্ষাগত চ্যালেঞ্জ হোক, চাপ হোক, বা ক্যারিয়ারের প্রশ্ন হোক।"
            }
        }
        
        # Simple keyword matching for demo
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['study', 'learn', 'exam', 'पढ़', 'অধ্যয়ন', 'পরীক্ষা']):
            return responses[language]['study']
        elif any(word in message_lower for word in ['stress', 'worried', 'anxious', 'तनाव', 'चिंता', 'চিন্তা', 'দুশ্চিন্তা']):
            return responses[language]['stress']
        elif any(word in message_lower for word in ['career', 'job', 'future', 'करियर', 'কর্মজীবন']):
            return responses[language]['career']
        else:
            return responses[language]['default']


class ScreeningAPIView(View):
    """Mental health screening endpoint"""
    
    def get(self, request):
        """Get screening questions"""
        screener_type = request.GET.get('type', 'GAD-2')
        
        # Demo questions
        questions = {
            'GAD-2': [
                {
                    'id': 'GAD2_1',
                    'text': 'Over the last 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?',
                    'options': [
                        {'value': 0, 'text': 'Not at all'},
                        {'value': 1, 'text': 'Several days'},
                        {'value': 2, 'text': 'More than half the days'},
                        {'value': 3, 'text': 'Nearly every day'}
                    ]
                },
                {
                    'id': 'GAD2_2',
                    'text': 'Over the last 2 weeks, how often have you been bothered by not being able to stop or control worrying?',
                    'options': [
                        {'value': 0, 'text': 'Not at all'},
                        {'value': 1, 'text': 'Several days'},
                        {'value': 2, 'text': 'More than half the days'},
                        {'value': 3, 'text': 'Nearly every day'}
                    ]
                }
            ],
            'PHQ-2': [
                {
                    'id': 'PHQ2_1',
                    'text': 'Over the last 2 weeks, how often have you been bothered by little interest or pleasure in doing things?',
                    'options': [
                        {'value': 0, 'text': 'Not at all'},
                        {'value': 1, 'text': 'Several days'},
                        {'value': 2, 'text': 'More than half the days'},
                        {'value': 3, 'text': 'Nearly every day'}
                    ]
                },
                {
                    'id': 'PHQ2_2',
                    'text': 'Over the last 2 weeks, how often have you been bothered by feeling down, depressed, or hopeless?',
                    'options': [
                        {'value': 0, 'text': 'Not at all'},
                        {'value': 1, 'text': 'Several days'},
                        {'value': 2, 'text': 'More than half the days'},
                        {'value': 3, 'text': 'Nearly every day'}
                    ]
                }
            ]
        }
        
        return JsonResponse({
            'screener_type': screener_type,
            'questions': questions.get(screener_type, [])
        })
    
    def post(self, request):
        """Submit screening responses"""
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id', 'demo_user')
            screener_type = data.get('screener_type', 'GAD-2')
            responses = data.get('responses', [])
            
            total_score = sum(responses)
            
            # Determine risk level
            if screener_type in ['GAD-2', 'PHQ-2']:
                risk_level = 'L3' if total_score >= 3 else 'L1'
            else:
                if total_score <= 4:
                    risk_level = 'L1'
                elif total_score <= 9:
                    risk_level = 'L2'
                else:
                    risk_level = 'L3'
            
            # Generate session ID
            session_id = f"SESS_{uuid.uuid4().hex[:8]}"
            
            # Generate actions based on risk level
            actions = self._generate_actions(risk_level)
            
            return JsonResponse({
                'session_id': session_id,
                'risk_level': risk_level,
                'total_score': total_score,
                'actions': actions,
                'recommendations': self._get_recommendations(risk_level)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _generate_actions(self, risk_level):
        """Generate actions based on risk level"""
        actions = {
            'L1': [
                {'text': 'Take a 5-minute walk outside', 'category': 'wellness', 'duration': 5},
                {'text': 'Review your study notes for 15 minutes', 'category': 'study', 'duration': 15},
                {'text': 'Listen to your favorite music', 'category': 'interest', 'duration': 10}
            ],
            'L2': [
                {'text': 'Practice deep breathing for 10 minutes', 'category': 'wellness', 'duration': 10},
                {'text': 'Connect with a friend or family member', 'category': 'social', 'duration': 20},
                {'text': 'Write in a journal about your feelings', 'category': 'wellness', 'duration': 15}
            ],
            'L3': [
                {'text': 'Try the 5-4-3-2-1 grounding technique', 'category': 'wellness', 'duration': 10},
                {'text': 'Contact campus counseling services', 'category': 'wellness', 'duration': 30},
                {'text': 'Talk to a trusted person about how you feel', 'category': 'social', 'duration': 30}
            ]
        }
        return actions.get(risk_level, [])
    
    def _get_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            'L1': [
                "Your responses indicate you're doing well overall.",
                "Continue practicing good self-care habits.",
                "Regular check-ins can help maintain your mental health."
            ],
            'L2': [
                "Your responses suggest you may benefit from additional support.",
                "Consider talking to a counselor or trusted person.",
                "Practice stress management techniques regularly."
            ],
            'L3': [
                "Your responses indicate significant concerns.",
                "We strongly recommend seeking professional support.",
                "Contact campus counseling or mental health services.",
                "Remember: seeking help is a sign of strength."
            ]
        }
        return recommendations.get(risk_level, [])


class PatternDetectionAPIView(View):
    """Pattern detection with k-anonymity"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            class_id = data.get('class_id')
            time_window = data.get('time_window', 7)
            
            # Load analytics data
            processor = CSVDataProcessor()
            patterns_df = processor.data.get('patterns', pd.DataFrame())
            
            # Filter patterns for the time window
            if not patterns_df.empty:
                patterns = patterns_df.head(10).to_dict('records')  # Show recent patterns
            else:
                patterns = self._generate_demo_patterns()
            
            return JsonResponse({
                'patterns': patterns,
                'class_id': class_id,
                'time_window': time_window
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _generate_demo_patterns(self):
        """Generate demo patterns for display"""
        return [
            {
                'pattern_type': 'temporal',
                'severity': 'medium',
                'k_count': 12,
                'pattern_data': {
                    'description': 'High stress levels detected during evening hours (6-8 PM)',
                    'affected_students': 12,
                    'time_pattern': 'weekday_evening'
                },
                'recommended_actions': ['Schedule study breaks', 'Offer evening wellness sessions']
            },
            {
                'pattern_type': 'academic',
                'severity': 'high',
                'k_count': 8,
                'pattern_data': {
                    'description': 'Decreased comprehension in advanced mathematics courses',
                    'affected_students': 8,
                    'subject': 'mathematics'
                },
                'recommended_actions': ['Additional tutoring', 'Review teaching methodology']
            }
        ]


class ActionViewSet(View):
    """Action management"""
    
    def get(self, request, action_id=None):
        """Get actions"""
        processor = CSVDataProcessor()
        actions_df = processor.data.get('actions', pd.DataFrame())
        
        if action_id:
            action = actions_df[actions_df['action_id'] == action_id]
            if not action.empty:
                return JsonResponse(action.iloc[0].to_dict())
            else:
                return JsonResponse({'error': 'Action not found'}, status=404)
        else:
            # Get query parameters
            student_id = request.GET.get('student_id')
            status_filter = request.GET.get('status')
            
            if student_id and not actions_df.empty:
                actions_df = actions_df[actions_df['student_id'] == student_id]
            
            if status_filter and not actions_df.empty:
                actions_df = actions_df[actions_df['status'] == status_filter]
            
            return JsonResponse({
                'actions': actions_df.to_dict('records') if not actions_df.empty else [],
                'count': len(actions_df) if not actions_df.empty else 0
            })
    
    def post(self, request):
        """Update action status"""
        try:
            data = json.loads(request.body)
            action_id = data.get('action_id')
            new_status = data.get('status')
            
            if not action_id or not new_status:
                return JsonResponse({'error': 'action_id and status are required'}, status=400)
            
            # For demo, just return success
            return JsonResponse({
                'success': True,
                'action_id': action_id,
                'new_status': new_status,
                'updated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StoreLocationView(View):
    """Store user location in session"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            accuracy = data.get('accuracy')
            
            if latitude is None or longitude is None:
                return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
            
            # Store location in session
            request.session['user_location'] = {
                'latitude': latitude,
                'longitude': longitude,
                'accuracy': accuracy,
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Location stored successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class InitChatView(View):
    """Initialize chat with location-based trending topics"""
    
    def post(self, request):
        try:
            from services.gemini_service import GeminiService
            
            data = json.loads(request.body)
            location_data = data.get('location', {})
            trending_topics = data.get('trending_topics', [])
            
            # Get user information for personalization
            username = None
            user_id = None
            
            # Try to get from authenticated user first
            if hasattr(request, 'user') and request.user.is_authenticated:
                username = request.user.username
                if hasattr(request.user, 'id'):
                    user_id = request.user.id
            
            # Fallback: try to get from request data
            if not username and not user_id:
                username = data.get('username')
                user_id = data.get('user_id') or data.get('student_id')
            
            # Initialize Gemini service
            gemini_service = GeminiService()
            
            # Always prioritize user's hometown from CSV over geolocation
            # Get user's hometown from CSV for personalized greeting
            from services.data_processing import CSVDataProcessor
            csv_processor = CSVDataProcessor()
            user_hometown = csv_processor.get_user_hometown(username=username, user_id=user_id)
            
            # Generate personalized greeting based on user's hometown and interests from CSV
            greeting = gemini_service.generate_personalized_greeting(
                username=username,
                user_id=user_id,
                language='English'
            )
            
            # Store initialization data in session
            request.session['chat_initialized'] = True
            request.session['initialization_data'] = {
                'user_hometown': user_hometown,
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'response': greeting,
                'topics': [],
                'location': user_hometown or 'your area'
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Init chat error: {str(e)}", exc_info=True)
            
            # Return fallback greeting
            fallback_message = "Hello! I'm Sahay, your AI wellness companion. I'm here to support your mental health and well-being through personalized conversations and guidance. How are you feeling today?"
            
            return JsonResponse({
                'success': True,
                'message': fallback_message,
                'topics': [],
                'location': 'Unknown'
            })


@method_decorator(csrf_exempt, name='dispatch')
class TopicInterestView(View):
    """Record user's interest in trending topics"""
    
    def post(self, request):
        try:
            from services.user_interests_service import user_interests_service
            
            data = json.loads(request.body)
            response_type = data.get('response')  # 'interested' or 'not_interested'
            topics = data.get('topics', [])
            
            if not response_type or not topics:
                return JsonResponse({'error': 'Response type and topics are required'}, status=400)
            
            # Get user information
            user_id = 1  # Default user ID for demo (Koushik Deb)
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = getattr(request.user, 'id', 1)
            
            # Get location information from session
            location = "Unknown"
            country = "US"
            if 'trending_data' in request.session:
                trending_data = request.session['trending_data']
                location = trending_data.get('location', 'Unknown')
                country = trending_data.get('country_code', 'US')
            
            # Record interest for each topic
            success_count = 0
            for topic in topics:
                if user_interests_service.add_user_interest(
                    user_id=user_id,
                    topic=topic,
                    interest=response_type,
                    location=location,
                    country=country,
                    source='trending'
                ):
                    success_count += 1
            
            return JsonResponse({
                'success': True,
                'recorded_interests': success_count,
                'total_topics': len(topics),
                'response_type': response_type
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Topic interest error: {str(e)}", exc_info=True)
            
            return JsonResponse({'error': str(e)}, status=500)
