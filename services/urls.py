from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('services/', views.services, name='services'),
    path('service-detail/<slug:slug>/', views.service_detail, name='service-detail'),
]
