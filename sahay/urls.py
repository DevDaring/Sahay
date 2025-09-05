"""
Django URL Configuration and Frontend Templates
"""

# ============================================
# sahay/urls.py - Main URL Configuration
# ============================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView, DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # App URLs
    path('api/', include('api.urls')),
    path('wellness/', include('wellness.urls')),
    path('learning/', include('learning.urls')),
    path('analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ============================================
# api/urls.py - API URL Configuration
# ============================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, ChatAPIView, ScreeningAPIView,
    PatternDetectionAPIView, ActionViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'actions', ActionViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('screening/', ScreeningAPIView.as_view(), name='screening'),
    path('patterns/', PatternDetectionAPIView.as_view(), name='patterns'),
]

# ============================================
# core/views.py - Core Django Views
# ============================================

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class HomeView(TemplateView):
    """Landing page view"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sahay - Your Wellness Companion'
        context['languages'] = ['English', 'Hindi', 'Bengali']
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add dashboard data
        from wellness.models import WellnessSession
        from core.models import Student
        
        context['total_students'] = Student.objects.count()
        context['recent_sessions'] = WellnessSession.objects.order_by('-created_at')[:10]
        return context

# ============================================
# wellness/views.py - Wellness Views
# ============================================

from django.views.generic import TemplateView, CreateView
from django.shortcuts import render, redirect
from .models import WellnessSession
from .forms import WellnessCheckInForm

class WellnessCheckInView(TemplateView):
    """Wellness check-in interface"""
    template_name = 'wellness/checkin.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mood_emojis'] = ['😊', '😐', '😔', '😰', '😡']
        return context

class ChatInterfaceView(TemplateView):
    """Chat interface with Gemini"""
    template_name = 'wellness/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_id'] = self.request.GET.get('student_id', '')
        return context

# ============================================
# learning/views.py - Learning Views
# ============================================

class CareerExplorerView(TemplateView):
    """Career exploration interface"""
    template_name = 'learning/career.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import CareerPath
        context['career_paths'] = CareerPath.objects.all()
        return context

class LearningDashboardView(TemplateView):
    """Learning progress dashboard"""
    template_name = 'learning/dashboard.html'

# ============================================
# analytics/views.py - Analytics Views
# ============================================

from django.views.generic import ListView
from .models import Pattern, AnonymousReport

class PatternListView(ListView):
    """View for pattern insights"""
    model = Pattern
    template_name = 'analytics/patterns.html'
    context_object_name = 'patterns'
    
    def get_queryset(self):
        return Pattern.objects.filter(k_count__gte=5).order_by('-created_at')

class ReportsView(ListView):
    """View for anonymous reports"""
    model = AnonymousReport
    template_name = 'analytics/reports.html'
    context_object_name = 'reports'