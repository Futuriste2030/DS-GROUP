#!/usr/bin/env python
"""Test réel envoi SMTP vers adresses équipe/RH"""
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

# Adresses équipe/RH depuis settings
CONTACT_EMAIL = getattr(settings, 'CONTACT_EMAIL', 'contact@bsgroup.ml')
HR_EMAIL = getattr(settings, 'HR_EMAIL', 'careers@bsgroup.ml')

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

print("=== TEST SMTP VERS EQUIPE/RH ===")
print(f"CONTACT_EMAIL: {CONTACT_EMAIL}")
print(f"HR_EMAIL: {HR_EMAIL}")
print()

try:
    # 1. Notification équipe contact
    html = render_to_string('email/mail-contact-team.html', {
        'nom': 'Aboulaye Macalou', 'email': 'abdoulaye208.mac@gmail.com',
        'telephone': '+223 00 00 00 00', 'service': 'Construction',
        'message': 'Test notification equipe contact',
        'reference': 'MS-TEST-001',
        'date': timezone.now().strftime('%d/%m/%Y a %H:%M'),
        'site_settings': None,
    })
    msg = EmailMultiAlternatives(
        'Nouvelle demande MS-TEST-001 - Construction',
        'Version texte', settings.DEFAULT_FROM_EMAIL, [CONTACT_EMAIL]
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print(f'SUCCES: Notification equipe envoyee a {CONTACT_EMAIL}')

    # 2. Notification équipe devis
    html = render_to_string('email/mail-quote-team.html', {
        'nom': 'Aboulaye Macalou', 'email': 'abdoulaye208.mac@gmail.com',
        'telephone': '+223 00 00 00 00', 'subject': 'Projet test',
        'message': 'Test notification equipe devis', 'location': 'Bamako',
        'size': '200 m2', 'budget': '50000-150000', 'timeline': '1-3 mois',
        'reference': 'QT-TEST-001',
        'date': timezone.now().strftime('%d/%m/%Y a %H:%M'),
        'site_settings': None,
    })
    msg = EmailMultiAlternatives(
        'Nouveau devis QT-TEST-001 - Projet test',
        'Version texte', settings.DEFAULT_FROM_EMAIL, [CONTACT_EMAIL]
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print(f'SUCCES: Notification equipe devis envoyee a {CONTACT_EMAIL}')

    # 3. Notification RH candidature
    html = render_to_string('email/mail-rh-career.html', {
        'prenom': 'Aboulaye', 'nom': 'Aboulaye Macalou', 'poste': 'Ingenieur Civil',
        'email': 'abdoulaye208.mac@gmail.com', 'telephone': '+223 00 00 00 00',
        'reference': 'BS-TEST-001', 'cv_url': '', 'message': 'Test candidature',
        'date': timezone.now().strftime('%d/%m/%Y a %H:%M'),
        'site_settings': None,
    })
    msg = EmailMultiAlternatives(
        f'Nouvelle candidature BS-TEST-001 - Ingenieur Civil',
        'Version texte', settings.DEFAULT_FROM_EMAIL, [HR_EMAIL]
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print(f'SUCCES: Notification RH envoyee a {HR_EMAIL}')

    print()
    print('Emails equipe/RH envoyes ! Verifie les boites:')
    print(f'  - {CONTACT_EMAIL} (contact + devis)')
    print(f'  - {HR_EMAIL} (candidatures)')

except Exception as e:
    print(f'ERREUR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()