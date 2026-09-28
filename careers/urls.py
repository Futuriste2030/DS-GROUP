from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    path('careers/', views.careers, name='careers'),
    path('career-detail/<slug:slug>/', views.career_detail, name='career-detail'),
    path('career-apply/', views.career_apply, name='career-apply'),
    path('career-success/', views.career_success, name='career-success'),
    path('career-success/<str:reference>/', views.career_success, name='career-success-detail'),
]
