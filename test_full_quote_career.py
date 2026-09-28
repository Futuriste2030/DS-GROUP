#!/usr/bin/env python
"""Test complet réel : soumission formulaire DEVIS + CANDIDATURE → emails via SMTP"""
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

# Forcer HR_EMAIL distinct pour le test
settings.HR_EMAIL = 'hr@bsgroup.ml'

from django.test import Client
from django.urls import reverse
from contact.models import QuoteRequest
from careers.models import Application, JobOpening

client = Client()

print("=== TEST COMPLET DEVIS + CANDIDATURE (SMTP REEL) ===")
print(f"User email: abdoulaye208.mac@gmail.com")
print(f"Team email (devis): {getattr(settings, 'CONTACT_EMAIL', 'contact@bsgroup.ml')}")
print(f"HR email (candidature): {settings.HR_EMAIL}")
print()

# ============================================================
# 1. TEST DEVIS
# ============================================================
print(">>> TEST DEVIS")
response = client.post(reverse('contact:devis'), {
    'projectType': 'Construction résidentielle',
    'location': 'Bamako, Mali',
    'size': '200 m2',
    'budget': '50,000 – 150,000',
    'timeline': 'Dans 1 – 3 mois',
    'message': 'Test devis complet avec SMTP reel',
    'name': 'Aboulaye Macalou',
    'email': 'abdoulaye208.mac@gmail.com',
    'phone': '+223 00 00 00 00',
}, HTTP_REFERER='http://testserver/devis/')

print(f"Status: {response.status_code}")
print(f"Redirect: {response.url}")

if response.status_code == 302:
    obj = QuoteRequest.objects.filter(email='abdoulaye208.mac@gmail.com').order_by('-created_at').first()
    if obj:
        print(f"Objet cree: {obj.reference} - {obj.name} - {obj.subject}")
        print()
        print("EMAILS DEVIS ENVOYES :")
        print(f"  1. Confirmation user -> abdoulaye208.mac@gmail.com")
        print(f"     Objet: 'Devis reçu — Réf. {obj.reference}'")
        print(f"     Template: mail-quote-confirm.html")
        print()
        print(f"  2. Notification equipe -> {getattr(settings, 'CONTACT_EMAIL', 'contact@bsgroup.ml')}")
        print(f"     Objet: 'Nouveau devis {obj.reference} — {obj.subject}'")
        print(f"     Template: mail-quote-team.html")

# ============================================================
# 2. TEST CANDIDATURE (avec job existant)
# ============================================================
print()
print(">>> TEST CANDIDATURE")
job = JobOpening.objects.first()
if not job:
    job = JobOpening.objects.create(
        title_fr='Ingénieur Civil Test',
        title_en='Civil Engineer Test',
        title_ar='مهندس مدني اختبار',
        slug='ingenieur-civil-test-hr',
        department='engineering',
        job_type='full_time',
        location_fr='Bamako, Mali',
        location_en='Bamako, Mali',
        location_ar='باماكو، مالي',
        description_fr='Poste de test HR',
        description_en='Test HR position',
        description_ar='منصب اختبار الموارد البشرية',
        salary='Compétitif',
        is_active=True,
    )
    print(f"Created test job: {job.title}")

response = client.post(reverse('careers:career-apply'), {
    'job_id': str(job.pk),
    'name': 'Aboulaye Macalou',
    'email': 'abdoulaye208.mac@gmail.com',
    'phone': '+223 00 00 00 00',
    'coverLetter': 'Test candidature complete avec SMTP reel vers hr@bsgroup.ml',
}, HTTP_REFERER='http://testserver/careers/')

print(f"Status: {response.status_code}")
print(f"Redirect: {response.url}")

if response.status_code == 302:
    app = Application.objects.filter(email='abdoulaye208.mac@gmail.com').order_by('-created_at').first()
    if app:
        print(f"Objet cree: {app.reference} - {app.full_name} - {app.job}")
        print()
        print("EMAILS CANDIDATURE ENVOYES :")
        print(f"  1. Confirmation user -> abdoulaye208.mac@gmail.com")
        print(f"     Objet: 'Candidature reçue — Réf. {app.reference}'")
        print(f"     Template: mail-career-confirm.html")
        print()
        print(f"  2. Notification RH -> {settings.HR_EMAIL}")
        print(f"     Objet: 'Nouvelle candidature {app.reference} — {app.job.title}'")
        print(f"     Template: mail-rh-career.html")

print()
print("=== VERIFIE LES 4 BOITES ===")
print("  1. abdoulaye208.mac@gmail.com -> 2 confirmations (devis + candidature)")
print("  2. contact@bsgroup.ml -> 1 notification devis")
print("  3. hr@bsgroup.ml -> 1 notification candidature")