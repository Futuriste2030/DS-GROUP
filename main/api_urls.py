from django.urls import path
from .views import cookie_consent

app_name = 'main_api'

urlpatterns = [
    path('cookie-consent/', cookie_consent, name='cookie_consent'),
]
