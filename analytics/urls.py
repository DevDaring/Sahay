from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsHomeView.as_view(), name='index'),
    path('patterns/', views.PatternDetectionView.as_view(), name='patterns'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('export/', views.ExportView.as_view(), name='export'),
]
