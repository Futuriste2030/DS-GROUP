#!/usr/bin/env python
"""Test complet réel : soumission formulaire contact → 2 emails via SMTP"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

# Config SMTP réelle
from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.EMAIL_HOST = 'bsgroup.ml'
settings.EMAIL_PORT = 465
settings.EMAIL_HOST_USER = 'noreply@bsgroup.ml'
settings.EMAIL_HOST_PASSWORD = 'Noreply@bsgroup223'
settings.EMAIL_USE_SSL = True
settings.EMAIL_USE_TLS = False
settings.DEFAULT_FROM_EMAIL = 'noreply@bsgroup.ml'

from django.test import Client
from django.urls import reverse
from contact.models import ContactMessage

client = Client()

print("=== TEST COMPLET FORMULAIRE CONTACT (SMTP REEL) ===")
print(f"User email: abdoulaye208.mac@gmail.com")
print(f"Team email: {getattr(settings, 'CONTACT_EMAIL', 'contact@bsgroup.ml')}")
print()

# Soumission formulaire contact
response = client.post(reverse('contact:contact'), {
    'name': 'Aboulaye',
    'lastName': 'Macalou',
    'email': 'abdoulaye208.mac@gmail.com',
    'phone': '+223 00 00 00 00',
    'subject': 'Test complet SMTP reel',
    'message': 'Ceci est un test complet de soumission du formulaire contact avec envoi SMTP reel.',
}, HTTP_REFERER='http://testserver/contact/')

print(f"Status: {response.status_code}")
print(f"Redirect: {response.url}")

if response.status_code == 302:
    # Vérifier l'objet créé en base
    obj = ContactMessage.objects.filter(email='abdoulaye208.mac@gmail.com').order_by('-created_at').first()
    if obj:
        print(f"Objet cree: {obj.reference} - {obj.name} - {obj.service}")
        print()
        print("EMAILS ENVOYES (verifie les 2 boites) :")
        print(f"  1. Confirmation user -> abdoulaye208.mac@gmail.com")
        print(f"     Objet: 'Demande reçue — Réf. {obj.reference}'")
        print(f"     Template: mail-contact-confirm.html")
        print()
        print(f"  2. Notification equipe -> {getattr(settings, 'CONTACT_EMAIL', 'contact@bsgroup.ml')}")
        print(f"     Objet: 'Nouvelle demande {obj.reference} — {obj.service}'")
        print(f"     Template: mail-contact-team.html")
        print()
        print("Verifie ta boite Gmail (et spams) ET la boite contact@bsgroup.ml")
    else:
        print("ERREUR: Objet non trouve en base")

# Follow redirect
if response.status_code == 302:
    response2 = client.get(response.url)
    print(f"Thanks page: {response2.status_code} - Reference visible: {obj.reference in response2.content.decode() if obj else False}")