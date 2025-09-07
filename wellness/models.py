"""
Wellness models - Simple version without duplicates
"""
from django.db import models
from core.models import BaseModel, Student
from django.core.validators import MinValueValidator, MaxValueValidator


class WellnessCheck(BaseModel):
    """Simple wellness check model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='wellness_checks')
    mood_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Mood score from 1-10"
    )
    notes = models.TextField(blank=True, help_text="Optional notes")
    
    class Meta:
        db_table = 'wellness_checks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wellness check for {self.student.student_id} - {self.mood_score}/10"
