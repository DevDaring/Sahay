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
from datetime import datetime, timedelta


class LearningHomeView(TemplateView):
    """Learning center main page"""
    template_name = 'learning/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        
        # Load learning data
        learning_df = processor.data.get('learning_sessions', pd.DataFrame())
        courses_df = processor.data.get('courses', pd.DataFrame())
        career_paths_df = processor.data.get('career_paths', pd.DataFrame())
        
        # Get learning statistics
        if not learning_df.empty:
            recent_sessions = learning_df[learning_df['created_at'] > (datetime.now() - timedelta(days=7))]
            
            context.update({
                'total_sessions': len(learning_df),
                'recent_sessions': len(recent_sessions),
                'avg_focus': float(learning_df['focus_score'].mean()) if 'focus_score' in learning_df.columns else 7.0,
                'popular_topics': learning_df['topic'].value_counts().head(5).to_dict() if 'topic' in learning_df.columns else {}
            })
        else:
            context.update({
                'total_sessions': 0,
                'recent_sessions': 0,
                'avg_focus': 7.0,
                'popular_topics': {}
            })
        
        # Get available courses
        courses_list = courses_df.to_dict('records') if not courses_df.empty else self._get_demo_courses()
        
        # Get career paths
        career_paths_list = career_paths_df.to_dict('records') if not career_paths_df.empty else self._get_demo_career_paths()
        
        context.update({
            'courses': courses_list[:6],  # Show first 6 courses
            'career_paths': career_paths_list[:4],  # Show first 4 career paths
            'study_tips': self._get_study_tips(),
            'quick_actions': [
                {'name': 'Start Study Session', 'url': '/learning/study/', 'icon': '📚', 'description': 'Begin focused study time'},
                {'name': 'Career Planning', 'url': '/learning/career/', 'icon': '🎯', 'description': 'Explore career paths'},
                {'name': 'Skill Assessment', 'url': '/learning/skills/', 'icon': '💡', 'description': 'Evaluate your abilities'},
                {'name': 'Study Tips', 'url': '/learning/tips/', 'icon': '🧠', 'description': 'AI-powered study advice'},
            ]
        })
        return context
    
    def _get_demo_courses(self):
        """Demo courses if CSV not available"""
        return [
            {'course_id': 'CS101', 'topic': 'Introduction to Programming', 'difficulty_level': 1},
            {'course_id': 'CS201', 'topic': 'Data Structures', 'difficulty_level': 2},
            {'course_id': 'CS301', 'topic': 'Algorithms', 'difficulty_level': 3},
            {'course_id': 'MA101', 'topic': 'Calculus I', 'difficulty_level': 2},
            {'course_id': 'PH101', 'topic': 'Physics Fundamentals', 'difficulty_level': 2},
            {'course_id': 'EE201', 'topic': 'Digital Electronics', 'difficulty_level': 3},
        ]
    
    def _get_demo_career_paths(self):
        """Demo career paths if CSV not available"""
        return [
            {
                'path_id': 'CP001',
                'field': 'Software Engineering',
                'required_skills': ['Programming', 'Problem Solving', 'System Design'],
                'typical_roles': ['Software Developer', 'Senior Engineer', 'Tech Lead']
            },
            {
                'path_id': 'CP002',
                'field': 'Data Science',
                'required_skills': ['Python', 'Statistics', 'Machine Learning'],
                'typical_roles': ['Data Analyst', 'Data Scientist', 'ML Engineer']
            },
            {
                'path_id': 'CP003',
                'field': 'Product Management',
                'required_skills': ['Strategy', 'Analytics', 'Communication'],
                'typical_roles': ['Associate PM', 'Product Manager', 'Senior PM']
            },
            {
                'path_id': 'CP004',
                'field': 'UI/UX Design',
                'required_skills': ['Design Thinking', 'Prototyping', 'User Research'],
                'typical_roles': ['UI Designer', 'UX Designer', 'Design Lead']
            }
        ]
    
    def _get_study_tips(self):
        """General study tips"""
        return [
            "Use the Pomodoro Technique: 25 minutes focused study, 5 minute break",
            "Create a dedicated study environment free from distractions",
            "Practice active recall instead of passive reading",
            "Form study groups to discuss concepts and solve problems together",
            "Take regular breaks to maintain concentration and avoid burnout"
        ]


class CareerPlanningView(TemplateView):
    """Career planning with dual-track approach"""
    template_name = 'learning/career.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        career_paths_df = processor.data.get('career_paths', pd.DataFrame())
        career_plans_df = processor.data.get('student_career_plans', pd.DataFrame())
        
        # Get all career paths
        career_paths = career_paths_df.to_dict('records') if not career_paths_df.empty else self._get_demo_career_paths()
        
        # Get student's current plan (demo data)
        current_plan = None
        if not career_plans_df.empty:
            current_plan = career_plans_df.iloc[0].to_dict()
        
        context.update({
            'career_paths': career_paths,
            'current_plan': current_plan,
            'dual_track_info': {
                'current_track': 'Optimize your current field with targeted skills',
                'explore_track': 'Explore new opportunities while building foundational skills'
            },
            'readiness_levels': [
                {'level': 'exploring', 'name': 'Exploring', 'description': 'Learning about different career options'},
                {'level': 'building', 'name': 'Building Skills', 'description': 'Actively developing required competencies'},
                {'level': 'ready', 'name': 'Ready to Apply', 'description': 'Prepared for job applications and interviews'},
                {'level': 'advanced', 'name': 'Advanced', 'description': 'Ready for senior roles and leadership'}
            ]
        })
        return context


class StudySessionView(TemplateView):
    """Study session tracker"""
    template_name = 'learning/study.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        processor = CSVDataProcessor()
        courses_df = processor.data.get('courses', pd.DataFrame())
        
        # Get available courses
        courses = courses_df.to_dict('records') if not courses_df.empty else self._get_demo_courses()
        
        context.update({
            'courses': courses,
            'session_types': [
                {'id': 'focused', 'name': 'Focused Study', 'description': 'Deep dive into specific topics', 'duration': 45},
                {'id': 'review', 'name': 'Review Session', 'description': 'Revisit and reinforce learned material', 'duration': 30},
                {'id': 'practice', 'name': 'Practice Problems', 'description': 'Apply knowledge through exercises', 'duration': 60},
                {'id': 'quick', 'name': 'Quick Recap', 'description': 'Brief overview of key concepts', 'duration': 15}
            ]
        })
        return context
    
    def post(self, request):
        """Handle study session submission"""
        try:
            course_id = request.POST.get('course_id')
            topic = request.POST.get('topic', '').strip()
            duration = int(request.POST.get('duration', 30))
            session_type = request.POST.get('session_type', 'focused')
            
            if not topic:
                messages.error(request, 'Topic is required')
                return redirect('learning:study')
            
            # For demo, just show success message
            messages.success(request, f'Study session "{topic}" recorded successfully!')
            
            return render(request, 'learning/study_success.html', {
                'topic': topic,
                'duration': duration,
                'session_type': session_type,
                'suggestions': self._get_study_suggestions(topic)
            })
            
        except Exception as e:
            messages.error(request, f'Error recording study session: {str(e)}')
            return redirect('learning:study')
    
    def _get_study_suggestions(self, topic):
        """Get AI-powered study suggestions"""
        return [
            f"Review {topic} concepts using active recall techniques",
            f"Find practice problems related to {topic}",
            f"Create mind maps or diagrams for {topic}",
            f"Discuss {topic} with study partners or online communities",
            f"Look for real-world applications of {topic}"
        ]


class StudyTipsView(TemplateView):
    """AI-powered study tips and advice"""
    template_name = 'learning/tips.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'tip_categories': [
                {
                    'name': 'Memory & Retention',
                    'tips': [
                        'Use spaced repetition to improve long-term retention',
                        'Create acronyms and mnemonics for complex information',
                        'Connect new information to existing knowledge',
                        'Teach concepts to others to reinforce your understanding'
                    ]
                },
                {
                    'name': 'Time Management',
                    'tips': [
                        'Use the Pomodoro Technique for focused study sessions',
                        'Prioritize tasks using the Eisenhower Matrix',
                        'Set specific, measurable study goals',
                        'Block out dedicated time for each subject'
                    ]
                },
                {
                    'name': 'Focus & Concentration',
                    'tips': [
                        'Eliminate distractions from your study environment',
                        'Use background music or white noise if helpful',
                        'Take regular breaks to avoid mental fatigue',
                        'Practice mindfulness to improve attention span'
                    ]
                },
                {
                    'name': 'Problem Solving',
                    'tips': [
                        'Break complex problems into smaller components',
                        'Use different problem-solving strategies',
                        'Practice with varied examples and scenarios',
                        'Review mistakes to understand error patterns'
                    ]
                }
            ],
            'ai_tips': [
                'Ask specific questions when you need help',
                'Use multiple sources to verify information',
                'Apply the Feynman Technique: explain concepts simply',
                'Create your own examples to test understanding'
            ]
        })
        return context
    
    def post(self, request):
        """Handle personalized tip requests"""
        try:
            subject = request.POST.get('subject', '').strip()
            difficulty = request.POST.get('difficulty', 'medium')
            learning_style = request.POST.get('learning_style', 'visual')
            
            # For demo, return personalized tips
            tips = self._get_personalized_tips(subject, difficulty, learning_style)
            
            return JsonResponse({
                'success': True,
                'tips': tips,
                'subject': subject,
                'difficulty': difficulty,
                'learning_style': learning_style
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    def _get_personalized_tips(self, subject, difficulty, learning_style):
        """Generate personalized study tips"""
        tips = []
        
        # Subject-specific tips
        if 'math' in subject.lower() or 'calculus' in subject.lower():
            tips.append('Practice problems daily to build muscle memory')
            tips.append('Understand the underlying concepts, not just procedures')
        elif 'programming' in subject.lower() or 'coding' in subject.lower():
            tips.append('Code along with examples and modify them')
            tips.append('Debug code systematically using print statements')
        elif 'science' in subject.lower() or 'physics' in subject.lower():
            tips.append('Visualize concepts with diagrams and models')
            tips.append('Connect theoretical concepts to real-world applications')
        
        # Difficulty-based tips
        if difficulty == 'easy':
            tips.append('Build confidence with basic concepts first')
        elif difficulty == 'hard':
            tips.append('Break complex topics into manageable chunks')
            tips.append('Seek help from instructors or study groups')
        
        # Learning style tips
        if learning_style == 'visual':
            tips.append('Use diagrams, charts, and color-coding')
        elif learning_style == 'auditory':
            tips.append('Record yourself explaining concepts')
        elif learning_style == 'kinesthetic':
            tips.append('Use hands-on activities and physical models')
        
        return tips[:5]  # Return top 5 tips
