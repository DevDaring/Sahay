"""
Learning models - Simple version without duplicates
"""
from django.db import models
from core.models import BaseModel, Student


class SimpleCourse(BaseModel):
    """Simple course model"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'simple_courses'
        ordering = ['title']
    
    def __str__(self):
        return self.title


class SimpleProgress(BaseModel):
    """Simple progress tracking"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='simple_progress')
    course = models.ForeignKey(SimpleCourse, on_delete=models.CASCADE)
    progress_percent = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'simple_progress'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.course.title} ({self.progress_percent}%)"
