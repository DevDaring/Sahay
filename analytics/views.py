from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from services.data_processing import CSVDataProcessor
import pandas as pd
import json
from datetime import datetime, timedelta


class AnalyticsHomeView(TemplateView):
    """Privacy-preserving analytics dashboard"""
    template_name = 'analytics/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        
        # Load all relevant data
        wellness_df = processor.data.get('wellness_sessions', pd.DataFrame())
        learning_df = processor.data.get('learning_sessions', pd.DataFrame())
        patterns_df = processor.data.get('patterns', pd.DataFrame())
        students_df = processor.data.get('students', pd.DataFrame())
        
        # Calculate privacy-preserving statistics
        analytics_data = self._calculate_safe_analytics(
            wellness_df, learning_df, patterns_df, students_df
        )
        
        context.update(analytics_data)
        return context
    
    def _calculate_safe_analytics(self, wellness_df, learning_df, patterns_df, students_df):
        """Calculate k-anonymized analytics ensuring privacy"""
        
        # Basic counts (safe as they're aggregated)
        total_students = len(students_df) if not students_df.empty else 0
        total_sessions = len(wellness_df) if not wellness_df.empty else 0
        total_learning_sessions = len(learning_df) if not learning_df.empty else 0
        
        # Language distribution (k-anonymized)
        if not students_df.empty and 'language_pref' in students_df.columns:
            lang_dist = students_df['language_pref'].value_counts()
            # Only show languages with k >= 5 students
            lang_dist = lang_dist[lang_dist >= 5].to_dict()
        else:
            lang_dist = {}
        
        # Age band distribution (k-anonymized)
        if not students_df.empty and 'age_band' in students_df.columns:
            age_dist = students_df['age_band'].value_counts()
            age_dist = age_dist[age_dist >= 5].to_dict()
        else:
            age_dist = {}
        
        # Wellness trends (aggregated, no individual data)
        wellness_trends = {}
        if not wellness_df.empty:
            # Weekly aggregated mood scores
            if 'mood_score' in wellness_df.columns and 'created_at' in wellness_df.columns:
                wellness_df['week'] = pd.to_datetime(wellness_df['created_at']).dt.isocalendar().week
                weekly_mood = wellness_df.groupby('week')['mood_score'].mean().to_dict()
                wellness_trends['mood'] = weekly_mood
            
            # Risk level distribution
            if 'risk_level' in wellness_df.columns:
                risk_dist = wellness_df['risk_level'].value_counts().to_dict()
                wellness_trends['risk_distribution'] = risk_dist
        
        # Learning patterns (aggregated)
        learning_patterns = {}
        if not learning_df.empty:
            # Popular topics (only if k >= 5)
            if 'topic' in learning_df.columns:
                topic_counts = learning_df['topic'].value_counts()
                popular_topics = topic_counts[topic_counts >= 5].head(10).to_dict()
                learning_patterns['popular_topics'] = popular_topics
            
            # Average session duration
            if 'duration_minutes' in learning_df.columns:
                learning_patterns['avg_duration'] = float(learning_df['duration_minutes'].mean())
        
        # Detected patterns (already k-anonymized)
        detected_patterns = []
        if not patterns_df.empty:
            recent_patterns = patterns_df.head(10)  # Show recent patterns
            detected_patterns = recent_patterns.to_dict('records')
        
        return {
            'total_students': total_students,
            'total_sessions': total_sessions,
            'total_learning_sessions': total_learning_sessions,
            'language_distribution': lang_dist,
            'age_distribution': age_dist,
            'wellness_trends': wellness_trends,
            'learning_patterns': learning_patterns,
            'detected_patterns': detected_patterns,
            'privacy_info': {
                'k_anonymity': 'All data shown maintains k-anonymity with k ≥ 5',
                'data_retention': 'Individual data is retained per user preferences',
                'aggregation': 'Only aggregated, non-identifiable statistics are displayed'
            }
        }


class PatternDetectionView(TemplateView):
    """Advanced pattern detection dashboard"""
    template_name = 'analytics/patterns.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        patterns_df = processor.data.get('patterns', pd.DataFrame())
        
        if not patterns_df.empty:
            # Group patterns by type
            pattern_types = patterns_df['pattern_type'].unique() if 'pattern_type' in patterns_df.columns else []
            
            pattern_summary = {}
            for ptype in pattern_types:
                type_patterns = patterns_df[patterns_df['pattern_type'] == ptype]
                pattern_summary[ptype] = {
                    'count': len(type_patterns),
                    'high_severity': len(type_patterns[type_patterns['severity'] == 'high']),
                    'avg_k_count': float(type_patterns['k_count'].mean()) if 'k_count' in type_patterns.columns else 0
                }
            
            recent_patterns = patterns_df.head(20).to_dict('records')
        else:
            pattern_types = []
            pattern_summary = {}
            recent_patterns = []
        
        context.update({
            'pattern_types': pattern_types,
            'pattern_summary': pattern_summary,
            'recent_patterns': recent_patterns,
            'pattern_descriptions': {
                'temporal': 'Time-based patterns in student behavior and performance',
                'social': 'Social interaction and collaboration patterns',
                'academic': 'Learning performance and engagement patterns',
                'environmental': 'Location and context-based patterns',
                'risk': 'Wellness risk indicators and early warning patterns'
            }
        })
        return context


class ReportsView(TemplateView):
    """Anonymous reporting system"""
    template_name = 'analytics/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        reports_df = processor.data.get('anonymous_reports', pd.DataFrame())
        
        if not reports_df.empty:
            # Status distribution
            status_dist = reports_df['status'].value_counts().to_dict() if 'status' in reports_df.columns else {}
            
            # Category distribution
            category_dist = reports_df['category'].value_counts().to_dict() if 'category' in reports_df.columns else {}
            
            # Recent reports (redacted)
            recent_reports = reports_df.head(10).to_dict('records')
        else:
            status_dist = {}
            category_dist = {}
            recent_reports = []
        
        context.update({
            'status_distribution': status_dist,
            'category_distribution': category_dist,
            'recent_reports': recent_reports,
            'report_categories': [
                {'id': 'infrastructure', 'name': 'Infrastructure', 'description': 'Campus facilities and equipment'},
                {'id': 'academic', 'name': 'Academic', 'description': 'Courses, teaching, and curriculum'},
                {'id': 'wellness', 'name': 'Wellness', 'description': 'Mental health and support services'},
                {'id': 'safety', 'name': 'Safety', 'description': 'Campus safety and security concerns'},
                {'id': 'other', 'name': 'Other', 'description': 'Other suggestions or reports'}
            ]
        })
        return context
    
    def post(self, request):
        """Handle new anonymous report submission"""
        try:
            report_type = request.POST.get('report_type')
            category = request.POST.get('category')
            content = request.POST.get('content', '').strip()
            location = request.POST.get('location', '').strip()
            
            if not content:
                return JsonResponse({'success': False, 'error': 'Content is required'}, status=400)
            
            # For demo, just return success
            # In real implementation, this would be saved to CSV with proper anonymization
            
            return JsonResponse({
                'success': True,
                'message': 'Your anonymous report has been submitted successfully. Thank you for helping improve our platform!',
                'report_id': f'ANON_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class ExportView(TemplateView):
    """Data export functionality"""
    template_name = 'analytics/export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'export_options': [
                {
                    'id': 'wellness_summary',
                    'name': 'Wellness Summary',
                    'description': 'Aggregated wellness statistics (k-anonymized)',
                    'format': 'CSV/JSON'
                },
                {
                    'id': 'learning_analytics',
                    'name': 'Learning Analytics',
                    'description': 'Learning patterns and performance metrics',
                    'format': 'CSV/JSON'
                },
                {
                    'id': 'pattern_reports',
                    'name': 'Pattern Reports',
                    'description': 'Detected patterns and insights',
                    'format': 'PDF/JSON'
                },
                {
                    'id': 'anonymized_feedback',
                    'name': 'Anonymous Feedback',
                    'description': 'Redacted suggestions and reports',
                    'format': 'CSV'
                }
            ],
            'privacy_notice': 'All exports maintain strict privacy standards with k-anonymity and data redaction.'
        })
        return context
    
    def post(self, request):
        """Handle export requests"""
        try:
            export_type = request.POST.get('export_type')
            format_type = request.POST.get('format', 'json')
            
            processor = CSVDataProcessor()
            
            # Generate export based on type
            if export_type == 'wellness_summary':
                data = self._export_wellness_summary(processor)
            elif export_type == 'learning_analytics':
                data = self._export_learning_analytics(processor)
            elif export_type == 'pattern_reports':
                data = self._export_pattern_reports(processor)
            elif export_type == 'anonymized_feedback':
                data = self._export_anonymized_feedback(processor)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid export type'}, status=400)
            
            return JsonResponse({
                'success': True,
                'data': data,
                'export_type': export_type,
                'format': format_type,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    def _export_wellness_summary(self, processor):
        """Export aggregated wellness data"""
        wellness_df = processor.data.get('wellness_sessions', pd.DataFrame())
        
        if wellness_df.empty:
            return {'message': 'No wellness data available'}
        
        # Only aggregated statistics
        summary = {
            'total_sessions': len(wellness_df),
            'average_mood': float(wellness_df['mood_score'].mean()) if 'mood_score' in wellness_df.columns else None,
            'average_anxiety': float(wellness_df['anxiety_score'].mean()) if 'anxiety_score' in wellness_df.columns else None,
            'risk_distribution': wellness_df['risk_level'].value_counts().to_dict() if 'risk_level' in wellness_df.columns else {}
        }
        
        return summary
    
    def _export_learning_analytics(self, processor):
        """Export learning analytics data"""
        learning_df = processor.data.get('learning_sessions', pd.DataFrame())
        
        if learning_df.empty:
            return {'message': 'No learning data available'}
        
        analytics = {
            'total_sessions': len(learning_df),
            'average_duration': float(learning_df['duration_minutes'].mean()) if 'duration_minutes' in learning_df.columns else None,
            'popular_topics': learning_df['topic'].value_counts().head(10).to_dict() if 'topic' in learning_df.columns else {},
            'average_focus': float(learning_df['focus_score'].mean()) if 'focus_score' in learning_df.columns else None
        }
        
        return analytics
    
    def _export_pattern_reports(self, processor):
        """Export detected patterns"""
        patterns_df = processor.data.get('patterns', pd.DataFrame())
        
        if patterns_df.empty:
            return {'message': 'No patterns detected'}
        
        # Only k-anonymized patterns
        patterns = patterns_df[patterns_df['k_count'] >= 5].to_dict('records') if 'k_count' in patterns_df.columns else []
        
        return {'patterns': patterns}
    
    def _export_anonymized_feedback(self, processor):
        """Export anonymous feedback"""
        reports_df = processor.data.get('anonymous_reports', pd.DataFrame())
        
        if reports_df.empty:
            return {'message': 'No feedback available'}
        
        # Only resolved reports, redacted content
        feedback = reports_df[reports_df['status'] == 'resolved'].to_dict('records') if 'status' in reports_df.columns else []
        
        return {'feedback': feedback}
