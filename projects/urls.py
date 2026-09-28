from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('projets/', views.projets, name='projets'),
    path('projet-detail/<slug:slug>/', views.projet_detail, name='projet-detail'),
]
