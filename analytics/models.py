"""
Analytics models - Simple version without duplicates
"""
from django.db import models
from core.models import BaseModel, Student


class SimpleAnalytics(BaseModel):
    """Simple analytics model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='simple_analytics')
    metric_name = models.CharField(max_length=100)
    metric_value = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'simple_analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.metric_name}: {self.metric_value}"
