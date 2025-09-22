"""
Django Admin Configuration - Simplified
"""
from django.contrib import admin
from core.models import Student
from wellness.models import WellnessCheck
from learning.models import SimpleCourse, SimpleProgress
from analytics.models import SimpleAnalytics

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'age_band', 'language_pref', 'enrollment_date']
    list_filter = ['age_band', 'language_pref']
    search_fields = ['student_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WellnessCheck)
class WellnessCheckAdmin(admin.ModelAdmin):
    list_display = ['student', 'mood_score', 'created_at']
    list_filter = ['mood_score', 'created_at']

@admin.register(SimpleCourse)
class SimpleCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']

@admin.register(SimpleProgress)
class SimpleProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percent']
    list_filter = ['progress_percent']

@admin.register(SimpleAnalytics)
class SimpleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'metric_name', 'metric_value']
    list_filter = ['metric_name']