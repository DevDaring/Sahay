"""
Django Admin Configuration and Management Commands
"""

# ============================================
# core/admin.py - Admin Interface Configuration
# ============================================

from django.contrib import admin
from django.utils.html import format_html
from core.models import Student, Course, Sahayak
from wellness.models import WellnessSession, Action, ScreeningQuestion
from learning.models import CareerPath, StudentCareerPlan, LearningSession
from analytics.models import Pattern, AnonymousReport, SahayakSession

# Custom Admin Site
class SahayAdminSite(admin.AdminSite):
    site_header = 'Sahay Administration'
    site_title = 'Sahay Admin'
    index_title = 'Welcome to Sahay Administration'

admin_site = SahayAdminSite(name='sahay_admin')

# Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'age_band', 'language_pref', 'enrollment_date', 'data_consent']
    list_filter = ['age_band', 'language_pref', 'data_consent']
    search_fields = ['student_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'age_band', 'enrollment_date')
        }),
        ('Preferences', {
            'fields': ('language_pref', 'interests')
        }),
        ('Privacy Settings', {
            'fields': ('data_consent', 'anonymous_sharing', 'retention_period')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_id', 'topic', 'difficulty_level', 'prerequisites_count']
    list_filter = ['difficulty_level']
    search_fields = ['course_id', 'topic']
    
    def prerequisites_count(self, obj):
        return len(obj.prerequisites) if obj.prerequisites else 0
    prerequisites_count.short_description = 'Prerequisites'

# Wellness Session Admin
@admin.register(WellnessSession)
class WellnessSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'student', 'risk_level', 'mood_score', 
                   'anxiety_score', 'created_at']
    list_filter = ['risk_level', 'needs_escalation', 'created_at']
    search_fields = ['session_id', 'student__student_id']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        # Ensure k-anonymity in admin view
        qs = super().get_queryset(request)
        return qs
    
    def risk_level_colored(self, obj):
        colors = {'L1': 'green', 'L2': 'orange', 'L3': 'red'}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.risk_level, 'black'),
            obj.risk_level
        )
    risk_level_colored.short_description = 'Risk Level'

# Action Admin
@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['action_id', 'student', 'category', 'status', 'due_date']
    list_filter = ['category', 'status', 'due_date']
    search_fields = ['action_id', 'student__student_id', 'action_text']
    actions = ['mark_completed', 'mark_skipped']
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = 'Mark selected actions as completed'
    
    def mark_skipped(self, request, queryset):
        queryset.update(status='skipped')
    mark_skipped.short_description = 'Mark selected actions as skipped'

# Pattern Admin (K-Anonymous View Only)
@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'severity', 'k_count', 'created_at']
    list_filter = ['pattern_type', 'severity', 'created_at']
    readonly_fields = ['pattern_data', 'recommended_actions', 'k_count']
    
    def has_add_permission(self, request):
        # Patterns are auto-generated, not manually added
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Patterns should not be deleted to maintain audit trail
        return False

# Career Path Admin
@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ['path_id', 'field', 'skills_count']
    search_fields = ['field', 'path_id']
    
    def skills_count(self, obj):
        return len(obj.required_skills) if obj.required_skills else 0
    skills_count.short_description = 'Required Skills'

# Sahayak Admin
@admin.register(Sahayak)
class SahayakAdmin(admin.ModelAdmin):
    list_display = ['mentor_id', 'name', 'rating', 'sessions_completed', 
                   'is_active', 'availability']
    list_filter = ['is_active', 'availability', 'rating']
    search_fields = ['name', 'mentor_id']
    actions = ['activate_mentors', 'deactivate_mentors']
    
    def activate_mentors(self, request, queryset):
        queryset.update(is_active=True)
    activate_mentors.short_description = 'Activate selected mentors'
    
    def deactivate_mentors(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_mentors.short_description = 'Deactivate selected mentors'

# ============================================
# management/commands/load_sample_data.py
# ============================================

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import random
import uuid

class Command(BaseCommand):
    help = 'Load sample CSV data into the database'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Load students
        self.load_students()
        
        # Load courses
        self.load_courses()
        
        # Load screening questions
        self.load_screening_questions()
        
        # Load career paths
        self.load_career_paths()
        
        # Load mentors
        self.load_sahayaks()
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
    
    def load_students(self):
        """Load students from CSV or generate sample data"""
        from core.models import Student
        
        if Student.objects.exists():
            self.stdout.write('Students already exist, skipping...')
            return
        
        interests_pool = [
            'cricket', 'music', 'coding', 'reading', 'gaming', 'art',
            'football', 'dance', 'photography', 'cooking', 'chess', 'debate'
        ]
        
        for i in range(50):
            student_interests = random.sample(interests_pool, k=random.randint(2, 5))
            Student.objects.create(
                student_id=f'STU{str(i+1).zfill(4)}',
                age_band=random.choice(['18-20', '20-22', '22-24']),
                language_pref=random.choice(['English', 'Hindi', 'Bengali']),
                interests=student_interests,
                enrollment_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                data_consent=True
            )
        
        self.stdout.write(f'Created {Student.objects.count()} students')
    
    def load_courses(self):
        """Load courses"""
        from core.models import Course
        
        if Course.objects.exists():
            self.stdout.write('Courses already exist, skipping...')
            return
        
        courses_data = [
            {'course_id': 'CS101', 'topic': 'Programming Fundamentals', 'difficulty_level': 1},
            {'course_id': 'CS102', 'topic': 'Data Structures', 'difficulty_level': 2},
            {'course_id': 'MATH201', 'topic': 'Linear Algebra', 'difficulty_level': 2},
            {'course_id': 'MATH202', 'topic': 'Calculus II', 'difficulty_level': 3},
            {'course_id': 'PHY101', 'topic': 'Physics I', 'difficulty_level': 2},
        ]
        
        for course_data in courses_data:
            Course.objects.create(**course_data)
        
        self.stdout.write(f'Created {Course.objects.count()} courses')
    
    def load_screening_questions(self):
        """Load screening questions"""
        from wellness.models import ScreeningQuestion
        
        if ScreeningQuestion.objects.exists():
            self.stdout.write('Screening questions already exist, skipping...')
            return
        
        questions = [
            {
                'question_id': 'GAD_1',
                'screener_type': 'GAD-2',
                'question_text': 'Over the last 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?',
                'scoring_rules': {
                    '0': 'Not at all',
                    '1': 'Several days',
                    '2': 'More than half the days',
                    '3': 'Nearly every day'
                },
                'order': 1
            },
            {
                'question_id': 'GAD_2',
                'screener_type': 'GAD-2',
                'question_text': 'Over the last 2 weeks, how often have you been bothered by not being able to stop or control worrying?',
                'scoring_rules': {
                    '0': 'Not at all',
                    '1': 'Several days',
                    '2': 'More than half the days',
                    '3': 'Nearly every day'
                },
                'order': 2
            }
        ]
        
        for q_data in questions:
            ScreeningQuestion.objects.create(**q_data)
        
        self.stdout.write(f'Created {ScreeningQuestion.objects.count()} screening questions')
    
    def load_career_paths(self):
        """Load career paths"""
        from learning.models import CareerPath
        
        if CareerPath.objects.exists():
            self.stdout.write('Career paths already exist, skipping...')
            return
        
        paths = [
            {
                'path_id': 'CAREER001',
                'field': 'Software Engineering',
                'required_skills': ['Programming', 'Problem Solving', 'Data Structures'],
                'typical_roles': ['Junior Developer', 'Software Engineer', 'Tech Lead'],
                'growth_trajectory': '2-3 years per level'
            },
            {
                'path_id': 'CAREER002',
                'field': 'Data Science',
                'required_skills': ['Statistics', 'Python', 'Machine Learning'],
                'typical_roles': ['Data Analyst', 'Data Scientist', 'ML Engineer'],
                'growth_trajectory': '2-4 years per level'
            }
        ]
        
        for path_data in paths:
            CareerPath.objects.create(**path_data)
        
        self.stdout.write(f'Created {CareerPath.objects.count()} career paths')
    
    def load_sahayaks(self):
        """Load mentors"""
        from core.models import Sahayak
        
        if Sahayak.objects.exists():
            self.stdout.write('Sahayaks already exist, skipping...')
            return
        
        expertise_areas = ['Programming', 'Mathematics', 'Career Guidance', 'Mental Wellness']
        
        for i in range(10):
            Sahayak.objects.create(
                mentor_id=f'MENT{str(i+1).zfill(3)}',
                name=f'Mentor {i+1}',
                expertise=random.sample(expertise_areas, k=random.randint(2, 3)),
                languages=['English', 'Hindi'],
                availability=random.choice(['Morning', 'Afternoon', 'Evening', 'Flexible']),
                rating=round(random.uniform(4.0, 5.0), 1),
                sessions_completed=random.randint(10, 100)
            )
        
        self.stdout.write(f'Created {Sahayak.objects.count()} mentors')

# ============================================
# management/commands/generate_patterns.py
# ============================================

class Command(BaseCommand):
    help = 'Generate pattern insights with k-anonymity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to analyze'
        )
    
    def handle(self, *args, **options):
        from wellness.models import WellnessSession
        from analytics.models import Pattern
        from django.conf import settings
        
        days = options['days']
        k_threshold = settings.K_ANONYMITY_THRESHOLD
        
        self.stdout.write(f'Analyzing patterns for last {days} days...')
        
        # Get recent sessions
        cutoff = timezone.now() - timedelta(days=days)
        sessions = WellnessSession.objects.filter(created_at__gte=cutoff)
        
        if sessions.count() < k_threshold:
            self.stdout.write(self.style.WARNING(
                f'Not enough data for k-anonymity (need {k_threshold}, have {sessions.count()})'
            ))
            return
        
        # Analyze risk patterns
        risk_counts = {}
        for session in sessions:
            if session.risk_level not in risk_counts:
                risk_counts[session.risk_level] = 0
            risk_counts[session.risk_level] += 1
        
        # Create patterns only if k-anonymity satisfied
        patterns_created = 0
        for risk_level, count in risk_counts.items():
            if count >= k_threshold:
                Pattern.objects.create(
                    pattern_type='risk',
                    k_count=count,
                    pattern_data={
                        'risk_level': risk_level,
                        'percentage': (count / sessions.count()) * 100
                    },
                    severity='high' if risk_level == 'L3' else 'medium',
                    time_window_days=days,
                    recommended_actions=['Increase support', 'Monitor closely']
                )
                patterns_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Created {patterns_created} patterns with k-anonymity preserved'
        ))

# ============================================
# management/commands/export_analytics.py
# ============================================

class Command(BaseCommand):
    help = 'Export analytics data to CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='data/output/analytics_export.csv',
            help='Output file path'
        )
    
    def handle(self, *args, **options):
        from wellness.models import WellnessSession
        from analytics.models import Pattern
        import pandas as pd
        
        output_path = options['output']
        
        # Aggregate data only (k-anonymous)
        sessions = WellnessSession.objects.all()
        
        # Create aggregated statistics
        stats = {
            'total_sessions': sessions.count(),
            'avg_mood_score': sessions.aggregate(avg=models.Avg('mood_score'))['avg'],
            'avg_anxiety_score': sessions.aggregate(avg=models.Avg('anxiety_score'))['avg'],
            'risk_distribution': {
                'L1': sessions.filter(risk_level='L1').count(),
                'L2': sessions.filter(risk_level='L2').count(),
                'L3': sessions.filter(risk_level='L3').count(),
            }
        }
        
        # Export to CSV
        df = pd.DataFrame([stats])
        df.to_csv(output_path, index=False)
        
        self.stdout.write(self.style.SUCCESS(
            f'Analytics exported to {output_path}'
        ))

# ============================================
# management/commands/cleanup_old_data.py
# ============================================

class Command(BaseCommand):
    help = 'Clean up old data based on retention policy'
    
    def handle(self, *args, **options):
        from django.conf import settings
        from wellness.models import WellnessSession
        
        retention_days = settings.DATA_RETENTION_DAYS
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Delete old sessions
        old_sessions = WellnessSession.objects.filter(created_at__lt=cutoff_date)
        count = old_sessions.count()
        
        if count > 0:
            old_sessions.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {count} sessions older than {retention_days} days'
            ))
        else:
            self.stdout.write('No old sessions to delete')