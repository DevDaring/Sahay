from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('students/', views.StudentViewSet.as_view(), name='students'),
    path('students/<int:student_id>/', views.StudentViewSet.as_view(), name='student-detail'),
    path('actions/', views.ActionViewSet.as_view(), name='actions'),
    path('chat/', views.ChatAPIView.as_view(), name='chat'),
    path('screening/', views.ScreeningAPIView.as_view(), name='screening'),
    path('patterns/', views.PatternDetectionAPIView.as_view(), name='patterns'),
    
    # Location-based endpoints
    path('store-location/', views.StoreLocationView.as_view(), name='store-location'),
    path('init-chat/', views.InitChatView.as_view(), name='init-chat'),
    path('topic-interest/', views.TopicInterestView.as_view(), name='topic-interest'),
]
