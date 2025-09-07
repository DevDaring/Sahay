from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import Student
from services.data_processing import CSVDataProcessor
import pandas as pd
from datetime import datetime, timedelta


class HomeView(TemplateView):
    """Main landing page for Sahay platform"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load CSV data for statistics
        processor = CSVDataProcessor()
        
        # Get basic stats
        students_df = processor.get_students()
        wellness_df = processor.data.get('wellness_sessions', pd.DataFrame())
        
        context.update({
            'total_students': len(students_df),
            'active_sessions': len(wellness_df[wellness_df['created_at'] > (datetime.now() - timedelta(days=7))]) if not wellness_df.empty else 0,
            'languages_supported': ['English', 'Hindi', 'Bengali'],
            'features': [
                {
                    'title': 'Multi-Language AI Support',
                    'description': 'Chat with Sahay in English, Hindi, or Bengali with culturally appropriate responses',
                    'icon': '🌍'
                },
                {
                    'title': 'Mental Health Screening',
                    'description': 'Privacy-preserving wellness assessments with immediate support',
                    'icon': '💚'
                },
                {
                    'title': 'Study Guidance',
                    'description': 'AI-powered learning tips with real-time internet search',
                    'icon': '📚'
                },
                {
                    'title': 'Career Planning',
                    'description': 'Dual-track career guidance with market insights',
                    'icon': '🚀'
                },
                {
                    'title': 'Privacy Protection',
                    'description': 'Complete anonymization with k-anonymity protection',
                    'icon': '🔒'
                },
                {
                    'title': 'Crisis Support',
                    'description': 'Immediate help with local emergency resources',
                    'icon': '🆘'
                }
            ]
        })
        return context


class DashboardView(TemplateView):
    """Main dashboard for logged-in users"""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load CSV data
        processor = CSVDataProcessor()
        
        # Get student data (for demo, using first student or creating a demo student)
        students_df = processor.get_students()
        if not students_df.empty:
            student_data = students_df.iloc[0].to_dict()
        else:
            student_data = {
                'student_id': 'DEMO_001',
                'age_band': '20-22',
                'language_pref': 'English',
                'interests': ['Technology', 'AI', 'Programming']
            }
        
        # Get recent wellness data
        wellness_df = processor.data.get('wellness_sessions', pd.DataFrame())
        recent_sessions = wellness_df.tail(5) if not wellness_df.empty else pd.DataFrame()
        
        # Get pending actions
        actions_df = processor.data.get('actions', pd.DataFrame())
        pending_actions = actions_df[actions_df['status'] == 'pending'].tail(5) if not actions_df.empty else pd.DataFrame()
        
        # Get learning progress
        learning_df = processor.data.get('learning_sessions', pd.DataFrame())
        recent_learning = learning_df.tail(5) if not learning_df.empty else pd.DataFrame()
        
        context.update({
            'student': student_data,
            'recent_sessions': recent_sessions.to_dict('records') if not recent_sessions.empty else [],
            'pending_actions': pending_actions.to_dict('records') if not pending_actions.empty else [],
            'recent_learning': recent_learning.to_dict('records') if not recent_learning.empty else [],
            'wellness_stats': self._get_wellness_stats(wellness_df),
            'quick_links': [
                {'name': 'Start Wellness Check', 'url': '/wellness/', 'icon': '💚'},
                {'name': 'Chat with Sahay', 'url': '/wellness/chat/', 'icon': '💬'},
                {'name': 'Career Planning', 'url': '/learning/career/', 'icon': '🎯'},
                {'name': 'Study Tips', 'url': '/learning/', 'icon': '📖'},
                {'name': 'View Analytics', 'url': '/analytics/', 'icon': '📊'},
            ]
        })
        return context
    
    def _get_wellness_stats(self, wellness_df):
        """Calculate wellness statistics from CSV data"""
        if wellness_df.empty:
            return {
                'avg_mood': 5.0,
                'avg_anxiety': 5.0,
                'risk_distribution': {'L1': 0, 'L2': 0, 'L3': 0},
                'trend': 'stable'
            }
        
        recent_week = wellness_df[wellness_df['created_at'] > (datetime.now() - timedelta(days=7))]
        
        return {
            'avg_mood': float(wellness_df['mood_score'].mean()) if 'mood_score' in wellness_df.columns else 5.0,
            'avg_anxiety': float(wellness_df['anxiety_score'].mean()) if 'anxiety_score' in wellness_df.columns else 5.0,
            'risk_distribution': wellness_df['risk_level'].value_counts().to_dict() if 'risk_level' in wellness_df.columns else {'L1': 0, 'L2': 0, 'L3': 0},
            'recent_sessions': len(recent_week),
            'trend': 'improving' if len(recent_week) > 0 else 'stable'
        }


class ProfileView(TemplateView):
    """User profile management"""
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load student data
        processor = CSVDataProcessor()
        students_df = processor.get_students()
        
        # For demo, use first student or create demo data
        if not students_df.empty:
            student_data = students_df.iloc[0].to_dict()
        else:
            student_data = {
                'student_id': 'DEMO_001',
                'age_band': '20-22',
                'language_pref': 'English',
                'interests': ['Technology', 'AI', 'Programming'],
                'data_consent': True,
                'anonymous_sharing': True,
                'retention_period': 90
            }
        
        context.update({
            'student': student_data,
            'language_choices': [
                ('English', 'English'),
                ('Hindi', 'हिन्दी'),
                ('Bengali', 'বাংলা'),
            ],
            'age_band_choices': [
                ('18-20', '18-20 years'),
                ('20-22', '20-22 years'),
                ('22-24', '22-24 years'),
                ('24+', '24+ years'),
            ],
            'privacy_info': {
                'data_protection': 'Your data is protected using k-anonymity and hash-based anonymization.',
                'retention': f"Data is retained for {student_data.get('retention_period', 90)} days.",
                'sharing': 'Anonymous sharing helps improve the platform for all students.' if student_data.get('anonymous_sharing') else 'Data is not shared anonymously.'
            }
        })
        return context
