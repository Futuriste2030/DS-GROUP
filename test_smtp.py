#!/usr/bin/env python
"""Test réel envoi SMTP via serveur du domaine (port 465 SSL)"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

# Override settings pour SMTP réel - config style DIGI-AGENCY
from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.EMAIL_HOST = 'bsgroup.ml'
settings.EMAIL_PORT = 465
settings.EMAIL_HOST_USER = 'noreply@bsgroup.ml'
settings.EMAIL_HOST_PASSWORD = 'Noreply@bsgroup223'
settings.EMAIL_USE_SSL = True
settings.EMAIL_USE_TLS = False
settings.DEFAULT_FROM_EMAIL = 'noreply@bsgroup.ml'

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

print("=== TEST SMTP REEL (SSL 465) ===")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT} (SSL)")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"To: abdoulaye208.mac@gmail.com")
print()

try:
    # Test simple d'abord
    msg = EmailMultiAlternatives(
        'Test SMTP SSL 465 - BS GROUP',
        'Version texte - Test SMTP reel SSL',
        settings.DEFAULT_FROM_EMAIL,
        ['abdoulaye208.mac@gmail.com']
    )
    msg.send()
    print('SUCCES: Email simple envoye')

    # Test 1: Contact confirm
    html = render_to_string('email/mail-contact-confirm.html', {
        'name': 'Aboulaye',
        'subject': 'Test SMTP reel SSL 465',
        'reference': 'MS-TEST-SSL-001'
    })
    msg = EmailMultiAlternatives(
        'Test SSL 465 - Contact Confirm BS GROUP',
        'Version texte - Test SMTP reel SSL',
        settings.DEFAULT_FROM_EMAIL,
        ['abdoulaye208.mac@gmail.com']
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print('SUCCES: Contact confirm envoye')

    # Test 2: Career confirm
    html = render_to_string('email/mail-career-confirm.html', {
        'name': 'Aboulaye',
        'job_title': 'Ingenieur Civil',
        'reference': 'BS-TEST-SSL-001'
    })
    msg = EmailMultiAlternatives(
        'Test SSL 465 - Career Confirm BS GROUP',
        'Version texte - Test SMTP reel SSL',
        settings.DEFAULT_FROM_EMAIL,
        ['abdoulaye208.mac@gmail.com']
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
    print('SUCCES: Career confirm envoye')

    print()
    print('Emails envoyes via SMTP SSL 465 ! Verifie ta boite (et spams).')

except Exception as e:
    print(f'ERREUR SMTP: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    print()
    print('Verifications:')
    print('1. Le serveur SMTP bsgroup.ml:465 accepte les connexions')
    print('2. Le mot de passe "Noreply@bsgroup223" est correct pour noreply@bsgroup.ml')
    print('3. Le certificat SSL est valide (ou EMAIL_SSL_CERTFILE/EMAIL_SSL_KEYFILE si auto-signe)')
    print('4. Pare-feu/antivirus ne bloque pas le port 465 sortant')