from django.urls import path
from . import views

app_name = 'wellness'

urlpatterns = [
    path('', views.WellnessHomeView.as_view(), name='index'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('check/', views.WellnessCheckView.as_view(), name='check'),
    path('screening/<str:screener_type>/', views.ScreeningView.as_view(), name='screening'),
]
