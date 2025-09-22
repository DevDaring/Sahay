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