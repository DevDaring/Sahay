"""
Django Models for Sahay Platform
Split across multiple apps for better organization
"""

# ============================================
# core/models.py - Core models
# ============================================

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Student(BaseModel):
    """Student model - extends Django User"""
    student_id = models.CharField(max_length=20, unique=True)
    age_band = models.CharField(max_length=10, choices=[
        ('18-20', '18-20 years'),
        ('20-22', '20-22 years'),
        ('22-24', '22-24 years'),
        ('24+', '24+ years'),
    ])
    language_pref = models.CharField(max_length=20, choices=[
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Bengali', 'Bengali'),
    ], default='English')
    interests = models.JSONField(default=list, help_text="List of student interests")
    enrollment_date = models.DateField()
    
    # Privacy settings
    data_consent = models.BooleanField(default=False)
    anonymous_sharing = models.BooleanField(default=True)
    retention_period = models.IntegerField(default=90, help_text="Data retention in days")
    
    class Meta:
        db_table = 'students'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['age_band', 'language_pref']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.age_band}"

class Course(BaseModel):
    """Course information"""
    course_id = models.CharField(max_length=20, unique=True)
    topic = models.CharField(max_length=200)
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    prerequisites = models.JSONField(default=list, help_text="List of prerequisite course IDs")
    
    class Meta:
        db_table = 'courses'
        ordering = ['difficulty_level', 'topic']
    
    def __str__(self):
        return f"{self.course_id}: {self.topic}"

class Sahayak(BaseModel):
    """Mentor/Sahayak model"""
    mentor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    expertise = models.JSONField(default=list)
    languages = models.JSONField(default=list)
    availability = models.CharField(max_length=50, choices=[
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
        ('Flexible', 'Flexible'),
    ])
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    sessions_completed = models.IntegerField(default=0)
    response_time_hours = models.IntegerField(default=24)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sahayaks'
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.mentor_id})"

# ============================================
# wellness/models.py - Wellness & Screening models
# ============================================

class ScreeningQuestion(BaseModel):
    """Mental health screening questions"""
    question_id = models.CharField(max_length=20, unique=True)
    screener_type = models.CharField(max_length=20, choices=[
        ('GAD-2', 'GAD-2'),
        ('GAD-7', 'GAD-7'),
        ('PHQ-2', 'PHQ-2'),
        ('PHQ-9', 'PHQ-9'),
        ('PC-PTSD-5', 'PC-PTSD-5'),
        ('AUDIT-C', 'AUDIT-C'),
    ])
    question_text = models.TextField()
    scoring_rules = models.JSONField(default=dict)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'screening_questions'
        ordering = ['screener_type', 'order']
    
    def __str__(self):
        return f"{self.screener_type}: {self.question_id}"

class WellnessSession(BaseModel):
    """Wellness check-in session"""
    session_id = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='wellness_sessions')
    
    # Scores (stored as aggregates only, no raw responses)
    mood_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    anxiety_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    screener_type = models.CharField(max_length=20, null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    
    # Risk assessment
    risk_level = models.CharField(max_length=5, choices=[
        ('L1', 'Low Risk'),
        ('L2', 'Medium Risk'),
        ('L3', 'High Risk'),
    ], default='L1')
    
    # Flags
    needs_escalation = models.BooleanField(default=False)
    escalated_to = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        db_table = 'wellness_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.student.student_id}"

class Action(BaseModel):
    """Personalized actions for students"""
    action_id = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='actions')
    session = models.ForeignKey(WellnessSession, on_delete=models.SET_NULL, null=True, blank=True)
    
    action_text = models.TextField()
    category = models.CharField(max_length=20, choices=[
        ('study', 'Study'),
        ('wellness', 'Wellness'),
        ('social', 'Social'),
        ('break', 'Break'),
        ('interest', 'Interest-based'),
    ])
    duration_minutes = models.IntegerField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('snoozed', 'Snoozed'),
    ], default='pending')
    
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'actions'
        ordering = ['due_date', 'status']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.category}: {self.action_text[:50]}"

# ============================================
# learning/models.py - Learning & Career models
# ============================================

class CareerPath(BaseModel):
    """Career path information"""
    path_id = models.CharField(max_length=20, unique=True)
    field = models.CharField(max_length=100)
    required_skills = models.JSONField(default=list)
    typical_roles = models.JSONField(default=list)
    growth_trajectory = models.TextField()
    
    class Meta:
        db_table = 'career_paths'
        ordering = ['field']
    
    def __str__(self):
        return self.field

class StudentCareerPlan(BaseModel):
    """Student's personalized career plan"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='career_plans')
    
    # Dual-track approach
    current_track = models.ForeignKey(
        CareerPath, on_delete=models.SET_NULL, 
        null=True, related_name='current_students'
    )
    explore_track = models.ForeignKey(
        CareerPath, on_delete=models.SET_NULL,
        null=True, related_name='exploring_students'
    )
    
    # Calibration metrics
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    feasibility_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Progress tracking
    skills_acquired = models.JSONField(default=list)
    next_steps = models.JSONField(default=list)
    proof_points = models.JSONField(default=list)
    
    # Readiness assessment
    readiness_level = models.CharField(max_length=20, choices=[
        ('exploring', 'Exploring'),
        ('building', 'Building Skills'),
        ('ready', 'Ready to Apply'),
        ('advanced', 'Advanced'),
    ], default='exploring')
    
    class Meta:
        db_table = 'student_career_plans'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.current_track.field if self.current_track else 'No track'}"

class LearningSession(BaseModel):
    """Learning micro-session tracking"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_sessions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    topic = models.CharField(max_length=200)
    duration_minutes = models.IntegerField()
    
    # Performance metrics
    quiz_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    comprehension_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], null=True, blank=True)
    
    # Engagement metrics
    focus_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    
    class Meta:
        db_table = 'learning_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['course', 'topic']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.topic}"

# ============================================
# analytics/models.py - Analytics & Pattern models
# ============================================

class Pattern(BaseModel):
    """Detected patterns (k-anonymized)"""
    pattern_type = models.CharField(max_length=50, choices=[
        ('temporal', 'Temporal Pattern'),
        ('social', 'Social Pattern'),
        ('academic', 'Academic Pattern'),
        ('environmental', 'Environmental Pattern'),
        ('risk', 'Risk Pattern'),
    ])
    
    # K-anonymity compliance
    k_count = models.IntegerField(
        validators=[MinValueValidator(5)],  # Minimum k-anonymity threshold
        help_text="Number of students in this pattern group"
    )
    
    # Pattern details
    pattern_data = models.JSONField(default=dict)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ])
    
    # Context
    class_id = models.CharField(max_length=50, null=True, blank=True)
    location_bucket = models.CharField(max_length=100, null=True, blank=True)
    time_window_days = models.IntegerField(default=7)
    
    # Recommendations
    recommended_actions = models.JSONField(default=list)
    
    class Meta:
        db_table = 'patterns'
        ordering = ['-created_at', 'severity']
        indexes = [
            models.Index(fields=['pattern_type', 'severity']),
            models.Index(fields=['class_id']),
        ]
    
    def __str__(self):
        return f"{self.pattern_type} - {self.severity} (k={self.k_count})"

class AnonymousReport(BaseModel):
    """Anonymous reports (for Suggest/Report feature)"""
    report_type = models.CharField(max_length=20, choices=[
        ('suggest', 'Suggestion'),
        ('report', 'Report'),
    ])
    
    category = models.CharField(max_length=50, choices=[
        ('infrastructure', 'Infrastructure'),
        ('academic', 'Academic'),
        ('wellness', 'Wellness'),
        ('safety', 'Safety'),
        ('other', 'Other'),
    ])
    
    # Anonymized location
    location_bucket = models.CharField(max_length=100)
    
    # K-anonymity
    k_count = models.IntegerField(
        validators=[MinValueValidator(5)],
        default=5
    )
    
    # Content (redacted)
    content_redacted = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('declined', 'Declined'),
    ], default='pending')
    
    handler = models.CharField(max_length=100, null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'anonymous_reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
        ]
    
    def __str__(self):
        return f"{self.report_type} - {self.category} ({self.status})"

class SahayakSession(BaseModel):
    """Mentor session tracking"""
    mentor = models.ForeignKey(Sahayak, on_delete=models.CASCADE, related_name='sessions')
    student_hash = models.CharField(max_length=64, help_text="Hashed student ID for privacy")
    
    # Session details
    duration_minutes = models.IntegerField()
    topic = models.CharField(max_length=200)
    
    # Summary (no transcripts stored)
    summary_bullets = models.JSONField(default=list)
    next_steps = models.JSONField(default=list)
    
    # Flags
    was_escalated = models.BooleanField(default=False)
    escalation_reason = models.CharField(max_length=200, null=True, blank=True)
    
    # Feedback
    student_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    class Meta:
        db_table = 'sahayak_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mentor', '-created_at']),
        ]
    
    def __str__(self):
        return f"Session with {self.mentor.name} - {self.topic}"