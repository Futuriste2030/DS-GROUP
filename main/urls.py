from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('faqs/', views.faqs, name='faqs'),
    path('cgu/', views.cgu, name='cgu'),
    path('cookies/', views.cookies, name='cookies'),
    path('legales/', views.legales, name='legales'),
    path('privacy/', views.privacy, name='privacy'),
    path('coming/', views.coming, name='coming'),
]
