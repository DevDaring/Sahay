from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.LearningHomeView.as_view(), name='index'),
    path('career/', views.CareerPlanningView.as_view(), name='career'),
    path('study/', views.StudySessionView.as_view(), name='study'),
    path('tips/', views.StudyTipsView.as_view(), name='tips'),
]
