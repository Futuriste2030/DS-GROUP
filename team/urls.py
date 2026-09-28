from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('team/', views.team, name='team'),
    path('team-detail/<slug:slug>/', views.team_detail, name='team-detail'),
    path('testimonials/', views.testimonials, name='testimonials'),
]
