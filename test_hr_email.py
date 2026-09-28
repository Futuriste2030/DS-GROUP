#!/usr/bin/env python
"""Test envoi SMTP vers hr@bsgroup.ml (notifications candidature)"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.EMAIL_HOST = 'bsgroup.ml'
settings.EMAIL_PORT = 465
settings.EMAIL_HOST_USER = 'noreply@bsgroup.ml'
settings.EMAIL_HOST_PASSWORD = 'Noreply@bsgroup223'
settings.EMAIL_USE_SSL = True
settings.EMAIL_USE_TLS = False
settings.DEFAULT_FROM_EMAIL = 'noreply@bsgroup.ml'

# HR_EMAIL depuis settings (avec fallback CAREERS_EMAIL)
HR_EMAIL = getattr(settings, 'HR_EMAIL', getattr(settings, 'CAREERS_EMAIL', 'careers@bsgroup.ml'))

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

print("=== TEST SMTP VERS HR_EMAIL ===")
print(f"HR_EMAIL: {HR_EMAIL}")
print()

try:
    # Notification RH candidature (template mail-rh-career.html)
    html = render_to_string('email/mail-rh-career.html', {
        'prenom': 'Aboulaye', 'nom': 'Aboulaye Macalou', 'poste': 'Ingenieur Civil',
        'email': 'abdoulaye208.mac@gmail.com', 'telephone': '+223 00 00 00 00',
        'reference': 'BS-TEST-HR-001', 'cv_url': '', 'message': 'Test notification HR',
        'date': timezone.now().strftime('%d/%m/%Y a %H:%M'),
        'site_settings': None,
    })
    msg = EmailMultiAlternatives(
        f'Nouvelle candidature BS-TEST-HR-001 - Ingenieur Civil',
        'Version texte', settings.DEFAULT_FROM_EMAIL, [HR_EMAIL]
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print(f'SUCCES: Notification RH envoyee a {HR_EMAIL}')

    print()
    print('Verifie la boite hr@bsgroup.ml (et spams)')

except Exception as e:
    print(f'ERREUR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()