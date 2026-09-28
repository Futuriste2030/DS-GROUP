from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('devis/', views.quote, name='devis'),
    path('thanks/', views.thanks, name='thanks'),
    path('thanks/<str:reference>/', views.thanks, name='thanks_detail'),
    path('thank-devis/', views.thank_devis, name='thank_devis'),
    path('thank-devis/<str:reference>/', views.thank_devis, name='thank_devis_detail'),
    path('newsletter/', views.newsletter, name='newsletter'),
]
