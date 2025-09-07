from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from services.data_processing import CSVDataProcessor
from services.gemini_service import GeminiService
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta


class WellnessHomeView(TemplateView):
    """Wellness center main page"""
    template_name = 'wellness/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        wellness_df = processor.data.get('wellness_sessions', pd.DataFrame())
        
        # Get wellness statistics
        if not wellness_df.empty:
            recent_sessions = wellness_df[wellness_df['created_at'] > (datetime.now() - timedelta(days=7))]
            
            context.update({
                'total_sessions': len(wellness_df),
                'recent_sessions': len(recent_sessions),
                'avg_mood': float(wellness_df['mood_score'].mean()) if 'mood_score' in wellness_df.columns else 5.0,
                'avg_anxiety': float(wellness_df['anxiety_score'].mean()) if 'anxiety_score' in wellness_df.columns else 5.0,
                'risk_distribution': wellness_df['risk_level'].value_counts().to_dict() if 'risk_level' in wellness_df.columns else {}
            })
        else:
            context.update({
                'total_sessions': 0,
                'recent_sessions': 0,
                'avg_mood': 5.0,
                'avg_anxiety': 5.0,
                'risk_distribution': {}
            })
        
        context.update({
            'screening_types': [
                {'id': 'GAD-2', 'name': 'Anxiety Screening (GAD-2)', 'description': 'Quick 2-question anxiety assessment', 'duration': '1 min'},
                {'id': 'GAD-7', 'name': 'Detailed Anxiety (GAD-7)', 'description': 'Comprehensive anxiety evaluation', 'duration': '3 min'},
                {'id': 'PHQ-2', 'name': 'Depression Screening (PHQ-2)', 'description': 'Quick depression check', 'duration': '1 min'},
                {'id': 'PHQ-9', 'name': 'Detailed Depression (PHQ-9)', 'description': 'Comprehensive depression assessment', 'duration': '4 min'},
            ]
        })
        return context


class ChatView(TemplateView):
    """Multi-language chat interface with Gemini AI"""
    template_name = 'wellness/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'languages': [
                {'code': 'en', 'name': 'English', 'native': 'English'},
                {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी'},
                {'code': 'bn', 'name': 'Bengali', 'native': 'বাংলা'},
            ],
            'chat_examples': {
                'en': [
                    "I'm feeling overwhelmed with my studies",
                    "Can you help me with study techniques?",
                    "I'm worried about my career prospects",
                    "I need some motivation today"
                ],
                'hi': [
                    "मुझे अपनी पढ़ाई का बहुत तनाव है",
                    "क्या आप मुझे पढ़ने की तकनीक बता सकते हैं?",
                    "मैं अपने करियर को लेकर चिंतित हूँ",
                    "मुझे आज कुछ प्रेरणा चाहिए"
                ],
                'bn': [
                    "আমি আমার পড়াশোনা নিয়ে চাপে আছি",
                    "আপনি কি আমাকে পড়ার কৌশল সাহায্য করতে পারেন?",
                    "আমি আমার ক্যারিয়ার নিয়ে চিন্তিত",
                    "আজ আমার কিছু অনুপ্রেরণা দরকার"
                ]
            }
        })
        return context
    
    def post(self, request):
        """Handle chat messages via AJAX"""
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            language = data.get('language', 'English')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Initialize Gemini service
            gemini_service = GeminiService()
            
            # Get AI response
            response = gemini_service.chat_with_student(
                student_id='demo_user',  # For demo purposes
                message=message,
                language=language,
                context={'source': 'web_chat'}
            )
            
            return JsonResponse({
                'response': response.get('response', ''),
                'detected_language': response.get('detected_language', language),
                'actions': response.get('actions', []),
                'resources': response.get('crisis_resources', []),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error processing message: {str(e)}'}, status=500)


class ScreeningView(TemplateView):
    """Mental health screening questionnaire"""
    template_name = 'wellness/screening.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        screener_type = self.kwargs.get('screener_type', 'GAD-2')
        
        # Load screening questions from CSV
        processor = CSVDataProcessor()
        questions_df = processor.data.get('screening_questions', pd.DataFrame())
        
        if not questions_df.empty:
            questions = questions_df[questions_df['screener_type'] == screener_type]
            questions_list = questions.sort_values('order').to_dict('records')
        else:
            # Fallback questions for demo
            questions_list = self._get_fallback_questions(screener_type)
        
        context.update({
            'screener_type': screener_type,
            'questions': questions_list,
            'screener_info': self._get_screener_info(screener_type)
        })
        return context
    
    def _get_screener_info(self, screener_type):
        """Get information about screening type"""
        info = {
            'GAD-2': {
                'name': 'GAD-2 Anxiety Screen',
                'description': 'A brief screening tool for anxiety disorders',
                'duration': '1-2 minutes',
                'scoring': 'Scores range from 0-6. Score ≥3 suggests anxiety disorder.'
            },
            'GAD-7': {
                'name': 'GAD-7 Anxiety Assessment',
                'description': 'Comprehensive anxiety disorder screening',
                'duration': '2-3 minutes',
                'scoring': 'Scores: 0-4 minimal, 5-9 mild, 10-14 moderate, 15-21 severe anxiety.'
            },
            'PHQ-2': {
                'name': 'PHQ-2 Depression Screen',
                'description': 'Brief depression screening questionnaire',
                'duration': '1-2 minutes',
                'scoring': 'Scores range from 0-6. Score ≥3 suggests depression screening.'
            },
            'PHQ-9': {
                'name': 'PHQ-9 Depression Assessment',
                'description': 'Comprehensive depression screening tool',
                'duration': '3-4 minutes',
                'scoring': 'Scores: 0-4 minimal, 5-9 mild, 10-14 moderate, 15-19 moderately severe, 20-27 severe.'
            }
        }
        return info.get(screener_type, {})
    
    def _get_fallback_questions(self, screener_type):
        """Fallback questions if CSV not available"""
        questions = {
            'GAD-2': [
                {
                    'question_id': 'GAD2_1',
                    'question_text': 'Over the last 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?',
                    'order': 1
                },
                {
                    'question_id': 'GAD2_2', 
                    'question_text': 'Over the last 2 weeks, how often have you been bothered by not being able to stop or control worrying?',
                    'order': 2
                }
            ],
            'PHQ-2': [
                {
                    'question_id': 'PHQ2_1',
                    'question_text': 'Over the last 2 weeks, how often have you been bothered by little interest or pleasure in doing things?',
                    'order': 1
                },
                {
                    'question_id': 'PHQ2_2',
                    'question_text': 'Over the last 2 weeks, how often have you been bothered by feeling down, depressed, or hopeless?',
                    'order': 2
                }
            ]
        }
        return questions.get(screener_type, [])
    
    def post(self, request, screener_type):
        """Handle screening form submission"""
        try:
            responses = []
            total_score = 0
            
            # Process responses
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    responses.append(int(value))
                    total_score += int(value)
            
            # Determine risk level
            if screener_type in ['GAD-2', 'PHQ-2']:
                risk_level = 'L3' if total_score >= 3 else 'L1'
            else:  # GAD-7, PHQ-9
                if total_score <= 4:
                    risk_level = 'L1'
                elif total_score <= 9:
                    risk_level = 'L2'
                else:
                    risk_level = 'L3'
            
            # Save to CSV (simplified for demo)
            session_id = str(uuid.uuid4())
            
            context = {
                'session_id': session_id,
                'screener_type': screener_type,
                'total_score': total_score,
                'risk_level': risk_level,
                'recommendations': self._get_recommendations(screener_type, risk_level, total_score),
                'resources': self._get_crisis_resources() if risk_level == 'L3' else []
            }
            
            return render(request, 'wellness/screening_results.html', context)
            
        except Exception as e:
            messages.error(request, f'Error processing screening: {str(e)}')
            return redirect('wellness:screening', screener_type=screener_type)
    
    def _get_recommendations(self, screener_type, risk_level, score):
        """Get personalized recommendations based on screening results"""
        recommendations = {
            'L1': [
                "Your scores indicate low risk. Keep up your current wellness practices!",
                "Consider regular check-ins to maintain your mental health",
                "Explore mindfulness or meditation practices",
                "Maintain a healthy sleep schedule"
            ],
            'L2': [
                "Your scores suggest some concern. Consider these actions:",
                "Talk to a counselor or mental health professional",
                "Practice stress management techniques",
                "Maintain social connections with friends and family",
                "Consider joining a support group"
            ],
            'L3': [
                "Your scores indicate significant concern. Please consider:",
                "Seek immediate support from a mental health professional",
                "Contact campus counseling services",
                "Reach out to trusted friends or family members",
                "Consider crisis support resources if needed"
            ]
        }
        return recommendations.get(risk_level, [])
    
    def _get_crisis_resources(self):
        """Crisis support resources"""
        return [
            {
                'name': 'National Suicide Prevention Lifeline (India)',
                'phone': '91-9820466726',
                'description': '24/7 crisis support'
            },
            {
                'name': 'KIRAN Mental Health Helpline',
                'phone': '1800-599-0019',
                'description': '24/7 toll-free mental health support'
            },
            {
                'name': 'Campus Counseling Services',
                'phone': 'Contact your institution',
                'description': 'On-campus mental health support'
            }
        ]


class WellnessCheckView(TemplateView):
    """Quick mood and wellness check"""
    template_name = 'wellness/check.html'
    
    def post(self, request):
        """Handle wellness check submission"""
        try:
            mood_score = int(request.POST.get('mood_score', 5))
            anxiety_score = int(request.POST.get('anxiety_score', 5))
            notes = request.POST.get('notes', '').strip()
            
            # Calculate combined score and risk level
            combined_score = mood_score + anxiety_score
            if combined_score <= 6:
                risk_level = 'L3'  # Low mood + high anxiety = higher risk
            elif combined_score <= 10:
                risk_level = 'L2'
            else:
                risk_level = 'L1'
            
            # Generate personalized actions based on scores
            actions = self._generate_actions(mood_score, anxiety_score, risk_level)
            
            context = {
                'mood_score': mood_score,
                'anxiety_score': anxiety_score,
                'risk_level': risk_level,
                'actions': actions,
                'session_id': str(uuid.uuid4()),
                'timestamp': datetime.now()
            }
            
            return render(request, 'wellness/check_results.html', context)
            
        except Exception as e:
            messages.error(request, f'Error processing wellness check: {str(e)}')
            return redirect('wellness:check')
    
    def _generate_actions(self, mood_score, anxiety_score, risk_level):
        """Generate personalized micro-actions"""
        actions = []
        
        if mood_score <= 3:  # Low mood
            actions.extend([
                {'text': 'Take 5 deep breaths slowly', 'category': 'wellness', 'duration': 2},
                {'text': 'Listen to your favorite uplifting song', 'category': 'interest', 'duration': 5},
                {'text': 'Write down 3 things you are grateful for', 'category': 'wellness', 'duration': 3}
            ])
        
        if anxiety_score <= 3:  # High anxiety
            actions.extend([
                {'text': 'Try the 5-4-3-2-1 grounding technique', 'category': 'wellness', 'duration': 5},
                {'text': 'Do 10 minutes of light stretching', 'category': 'wellness', 'duration': 10},
                {'text': 'Call or text a supportive friend', 'category': 'social', 'duration': 10}
            ])
        
        if mood_score >= 7 and anxiety_score >= 7:  # Good state
            actions.extend([
                {'text': 'Review notes for 15 minutes', 'category': 'study', 'duration': 15},
                {'text': 'Plan tomorrow\'s schedule', 'category': 'study', 'duration': 10},
                {'text': 'Explore a new topic of interest', 'category': 'interest', 'duration': 20}
            ])
        
        return actions[:3]  # Return top 3 actions
