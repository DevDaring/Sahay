"""
Django Views and API endpoints for Sahay Platform
"""

# ============================================
# api/serializers.py - REST Framework Serializers
# ============================================

from rest_framework import serializers
from core.models import Student, Course, Sahayak
from wellness.models import WellnessSession, Action, ScreeningQuestion
from learning.models import CareerPath, StudentCareerPlan, LearningSession
from analytics.models import Pattern, AnonymousReport

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'age_band', 'language_pref', 'interests', 'enrollment_date']
        read_only_fields = ['id']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_id', 'topic', 'difficulty_level', 'prerequisites']

class SahayakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sahayak
        fields = ['id', 'mentor_id', 'name', 'expertise', 'languages', 
                 'availability', 'rating', 'sessions_completed']

class WellnessSessionSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = WellnessSession
        fields = ['id', 'session_id', 'student_id', 'mood_score', 'anxiety_score',
                 'screener_type', 'total_score', 'risk_level', 'created_at']
        read_only_fields = ['id', 'session_id', 'risk_level', 'created_at']
    
    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        student = Student.objects.get(student_id=student_id)
        validated_data['student'] = student
        
        # Calculate risk level
        total = (validated_data.get('mood_score', 5) + 
                validated_data.get('anxiety_score', 5))
        
        if total <= 6:
            validated_data['risk_level'] = 'L1'
        elif total <= 10:
            validated_data['risk_level'] = 'L2'
        else:
            validated_data['risk_level'] = 'L3'
        
        return super().create(validated_data)

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'action_id', 'action_text', 'category', 
                 'duration_minutes', 'status', 'due_date']
        read_only_fields = ['id', 'action_id']

class ChatMessageSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    message = serializers.CharField()
    language = serializers.CharField(default='English')
    context = serializers.JSONField(required=False)

class ScreeningResponseSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    screener_type = serializers.CharField()
    responses = serializers.ListField(child=serializers.IntegerField())

class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ['id', 'pattern_type', 'k_count', 'pattern_data', 
                 'severity', 'recommended_actions', 'created_at']

# ============================================
# api/views.py - API Views
# ============================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Q
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
from .services import GeminiService, PatternDetector, ActionGenerator

class StudentViewSet(viewsets.ModelViewSet):
    """Student CRUD operations"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    
    @action(detail=True, methods=['post'])
    def wellness_checkin(self, request, student_id=None):
        """Wellness check-in for a student"""
        student = self.get_object()
        serializer = WellnessSessionSerializer(data=request.data)
        
        if serializer.is_valid():
            session = serializer.save(student=student, 
                                    session_id=f"SESS{uuid.uuid4().hex[:8]}")
            
            # Generate actions based on wellness scores
            action_gen = ActionGenerator()
            actions = action_gen.generate_for_session(session)
            
            return Response({
                'session': WellnessSessionSerializer(session).data,
                'actions': ActionSerializer(actions, many=True).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def career_plan(self, request, student_id=None):
        """Get student's career plan"""
        student = self.get_object()
        plan = StudentCareerPlan.objects.filter(student=student).first()
        
        if plan:
            return Response({
                'current_track': plan.current_track.field if plan.current_track else None,
                'explore_track': plan.explore_track.field if plan.explore_track else None,
                'confidence_score': plan.confidence_score,
                'feasibility_score': plan.feasibility_score,
                'next_steps': plan.next_steps
            })
        return Response({'message': 'No career plan found'}, 
                       status=status.HTTP_404_NOT_FOUND)

class ChatAPIView(APIView):
    """Chat endpoint for Gemini integration"""
    
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Get Gemini response
            gemini_service = GeminiService()
            response = gemini_service.generate_response(
                student_id=serializer.validated_data['student_id'],
                message=serializer.validated_data['message'],
                language=serializer.validated_data.get('language', 'English'),
                context=serializer.validated_data.get('context', {})
            )
            
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScreeningAPIView(APIView):
    """Mental health screening endpoint"""
    
    def get(self, request):
        """Get screening questions"""
        screener_type = request.query_params.get('type', 'GAD-2')
        questions = ScreeningQuestion.objects.filter(screener_type=screener_type)
        
        return Response({
            'screener_type': screener_type,
            'questions': [
                {
                    'id': q.question_id,
                    'text': q.question_text,
                    'options': q.scoring_rules
                }
                for q in questions
            ]
        })
    
    def post(self, request):
        """Submit screening responses"""
        serializer = ScreeningResponseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Calculate scores
            total_score = sum(data['responses'])
            
            # Determine risk level
            if total_score <= 6:
                risk_level = 'L1'
            elif total_score <= 10:
                risk_level = 'L2'
            else:
                risk_level = 'L3'
            
            # Create wellness session
            student = get_object_or_404(Student, student_id=data['student_id'])
            session = WellnessSession.objects.create(
                session_id=f"SESS{uuid.uuid4().hex[:8]}",
                student=student,
                screener_type=data['screener_type'],
                total_score=total_score,
                risk_level=risk_level
            )
            
            # Generate actions
            action_gen = ActionGenerator()
            actions = action_gen.generate_for_session(session)
            
            return Response({
                'session_id': session.session_id,
                'risk_level': risk_level,
                'total_score': total_score,
                'actions': ActionSerializer(actions, many=True).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatternDetectionAPIView(APIView):
    """Pattern detection with k-anonymity"""
    
    def post(self, request):
        """Detect patterns for a class/group"""
        class_id = request.data.get('class_id')
        time_window = request.data.get('time_window', 7)
        
        detector = PatternDetector()
        patterns = detector.detect_patterns(
            class_id=class_id,
            time_window_days=time_window
        )
        
        return Response(PatternSerializer(patterns, many=True).data)

class ActionViewSet(viewsets.ModelViewSet):
    """Action management"""
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student__student_id=student_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark action as completed"""
        action = self.get_object()
        action.status = 'completed'
        action.completed_at = timezone.now()
        action.save()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze action for later"""
        action = self.get_object()
        action.status = 'snoozed'
        action.due_date = timezone.now() + timedelta(hours=2)
        action.save()
        return Response({'status': 'snoozed', 'new_due_date': action.due_date})

# ============================================
# api/services.py - Business Logic Services
# ============================================

import vertexai
from vertexai.generative_models import GenerativeModel
from django.conf import settings
import hashlib

class GeminiService:
    """Service for Gemini AI integration"""
    
    def __init__(self):
        vertexai.init(project=settings.GCP_PROJECT_ID, 
                      location=settings.GCP_LOCATION)
        self.model = GenerativeModel(settings.VERTEX_AI_MODEL)
    
    def generate_response(self, student_id, message, language='English', context=None):
        """Generate AI response for student message"""
        try:
            # Get student info
            student = Student.objects.get(student_id=student_id)
            interests = ', '.join(student.interests)
            
            # Build prompt
            prompt = f"""
            You are Sahay, a friendly student wellness companion.
            Student interests: {interests}
            Language preference: {language}
            
            Student message: {message}
            
            Provide a supportive, encouraging response in {language}.
            Keep it brief and conversational.
            """
            
            # Add context if provided
            if context:
                if context.get('mood_score'):
                    prompt += f"\nStudent's mood: {context['mood_score']}/10"
                if context.get('anxiety_score'):
                    prompt += f"\nStudent's anxiety: {context['anxiety_score']}/10"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            return {
                'response': response.text,
                'session_id': f"CHAT{uuid.uuid4().hex[:8]}",
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            return {
                'response': "I'm here to help! How can I support you today?",
                'error': str(e)
            }

class PatternDetector:
    """Pattern detection service with k-anonymity"""
    
    def __init__(self):
        self.k_threshold = settings.K_ANONYMITY_THRESHOLD
    
    def detect_patterns(self, class_id, time_window_days=7):
        """Detect patterns while maintaining k-anonymity"""
        patterns = []
        
        # Get recent sessions
        cutoff = timezone.now() - timedelta(days=time_window_days)
        sessions = WellnessSession.objects.filter(
            created_at__gte=cutoff
        )
        
        if sessions.count() < self.k_threshold:
            return []
        
        # Temporal patterns
        temporal = self._detect_temporal_patterns(sessions)
        patterns.extend(temporal)
        
        # Risk patterns
        risk = self._detect_risk_patterns(sessions)
        patterns.extend(risk)
        
        # Academic patterns (if class_id provided)
        if class_id:
            academic = self._detect_academic_patterns(class_id, sessions)
            patterns.extend(academic)
        
        return patterns
    
    def _detect_temporal_patterns(self, sessions):
        """Detect time-based patterns"""
        patterns = []
        
        # Group by hour of day
        hour_groups = {}
        for session in sessions:
            hour = session.created_at.hour
            if hour not in hour_groups:
                hour_groups[hour] = []
            hour_groups[hour].append(session)
        
        # Check k-anonymity and create patterns
        for hour, group_sessions in hour_groups.items():
            if len(group_sessions) >= self.k_threshold:
                avg_anxiety = np.mean([s.anxiety_score for s in group_sessions 
                                      if s.anxiety_score])
                
                if avg_anxiety > 6:
                    pattern = Pattern.objects.create(
                        pattern_type='temporal',
                        k_count=len(group_sessions),
                        pattern_data={
                            'hour': hour,
                            'avg_anxiety': float(avg_anxiety),
                            'pattern': 'high_stress_hour'
                        },
                        severity='medium' if avg_anxiety > 7 else 'low',
                        recommended_actions=['Schedule breaks', 'Relaxation exercises']
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_risk_patterns(self, sessions):
        """Detect risk level patterns"""
        patterns = []
        
        # Group by risk level
        risk_counts = sessions.values('risk_level').annotate(
            count=Count('id')
        )
        
        for risk_data in risk_counts:
            if risk_data['count'] >= self.k_threshold:
                severity = 'high' if risk_data['risk_level'] == 'L3' else 'medium'
                
                pattern = Pattern.objects.create(
                    pattern_type='risk',
                    k_count=risk_data['count'],
                    pattern_data={
                        'risk_level': risk_data['risk_level'],
                        'percentage': (risk_data['count'] / sessions.count()) * 100
                    },
                    severity=severity,
                    recommended_actions=self._get_risk_actions(risk_data['risk_level'])
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_academic_patterns(self, class_id, sessions):
        """Detect academic-related patterns"""
        patterns = []
        
        # Get learning sessions for the class
        learning_sessions = LearningSession.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if learning_sessions.count() >= self.k_threshold:
            # Check comprehension levels
            low_comprehension = learning_sessions.filter(
                comprehension_level='low'
            ).count()
            
            if low_comprehension >= self.k_threshold:
                pattern = Pattern.objects.create(
                    pattern_type='academic',
                    k_count=low_comprehension,
                    class_id=class_id,
                    pattern_data={
                        'issue': 'low_comprehension',
                        'percentage': (low_comprehension / learning_sessions.count()) * 100
                    },
                    severity='high' if low_comprehension > self.k_threshold * 2 else 'medium',
                    recommended_actions=['Review teaching methods', 'Additional practice sessions']
                )
                patterns.append(pattern)
        
        return patterns
    
    def _get_risk_actions(self, risk_level):
        """Get recommended actions based on risk level"""
        actions = {
            'L1': ['Continue regular check-ins', 'Encourage positive activities'],
            'L2': ['Increase support', 'Suggest wellness resources', 'Connect with peer support'],
            'L3': ['Priority support', 'Professional counseling referral', 'Daily check-ins']
        }
        return actions.get(risk_level, [])

class ActionGenerator:
    """Generate personalized actions for students"""
    
    def generate_for_session(self, session):
        """Generate actions based on wellness session"""
        actions = []
        
        # Determine action categories based on risk level
        if session.risk_level == 'L3':
            categories = ['wellness', 'social', 'break']
        elif session.risk_level == 'L2':
            categories = ['wellness', 'study', 'interest']
        else:
            categories = ['study', 'wellness', 'interest']
        
        # Create actions
        for category in categories[:3]:  # Max 3 actions
            action = Action.objects.create(
                action_id=f"ACT{uuid.uuid4().hex[:8]}",
                student=session.student,
                session=session,
                action_text=self._get_action_text(category, session.student),
                category=category,
                duration_minutes=self._get_duration(category),
                due_date=timezone.now() + timedelta(hours=24)
            )
            actions.append(action)
        
        return actions
    
    def _get_action_text(self, category, student):
        """Get personalized action text"""
        templates = {
            'study': [
                "Complete a 15-minute focused study session",
                "Review today's notes and create a summary",
                "Solve 5 practice problems"
            ],
            'wellness': [
                "Take a 5-minute breathing exercise",
                "Go for a 10-minute walk",
                "Write 3 things you're grateful for"
            ],
            'social': [
                "Connect with a study buddy",
                "Join a group study session",
                "Help a peer with a concept"
            ],
            'break': [
                "Listen to your favorite music for 5 minutes",
                "Do some light stretching",
                "Have a healthy snack"
            ],
            'interest': [
                f"Spend 15 minutes on {student.interests[0] if student.interests else 'your hobby'}",
                "Read an article about your interests",
                "Work on a personal project"
            ]
        }
        
        import random
        return random.choice(templates.get(category, ["Take a break"]))
    
    def _get_duration(self, category):
        """Get action duration based on category"""
        durations = {
            'study': 20,
            'wellness': 10,
            'social': 30,
            'break': 5,
            'interest': 15
        }
        return durations.get(category, 10)