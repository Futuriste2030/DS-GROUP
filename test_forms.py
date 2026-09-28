#!/usr/bin/env python
"""Test contact and career form submissions"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from contact.models import ContactMessage
from careers.models import Application, JobOpening

client = Client()

print("=== TEST CONTACT FORM ===")
response = client.post(reverse('contact:contact'), {
    'name': 'Aboulaye',
    'lastName': 'Macalou',
    'email': 'abdoulaye208.mac@gmail.com',
    'phone': '+223 00 00 00 00',
    'subject': 'Test contact depuis script',
    'message': 'Ceci est un message de test pour verifier le formulaire de contact.',
}, HTTP_REFERER='http://testserver/contact/')

print(f"Status: {response.status_code}")
print(f"Redirect URL: {response.url}")

if response.status_code == 302:
    response2 = client.get(response.url)
    print(f"Thanks page status: {response2.status_code}")
    content = response2.content.decode()
    print(f"Reference in page: {'MS-' in content}")

print()
print("=== TEST CAREER APPLICATION ===")
job = JobOpening.objects.first()
if not job:
    job = JobOpening.objects.create(
        title_fr='Ingénieur Civil',
        title_en='Civil Engineer',
        title_ar='مهندس مدني',
        slug='ingenieur-civil-test',
        department='engineering',
        job_type='full_time',
        location_fr='Bamako, Mali',
        location_en='Bamako, Mali',
        location_ar='باماكو، مالي',
        description_fr='Poste de test pour validation formulaire',
        description_en='Test position for form validation',
        description_ar='منصب اختبار للتحقق من النموذج',
        salary='Compétitif',
        is_active=True,
    )
    print(f"Created test job: {job.title} (slug: {job.slug})")
else:
    print(f"Using existing job: {job.title} (slug: {job.slug})")

# career_apply expects job_id in POST (pk), not slug in URL
response = client.post(reverse('careers:career-apply'), {
    'job_id': str(job.pk),
    'name': 'Aboulaye Macalou',
    'email': 'abdoulaye208.mac@gmail.com',
    'phone': '+223 00 00 00 00',
    'coverLetter': 'Je suis tres interesse par ce poste. Voici ma lettre de motivation.',
}, HTTP_REFERER='http://testserver/careers/')

print(f"Status: {response.status_code}")
print(f"Redirect URL: {response.url}")

if response.status_code == 302:
    response2 = client.get(response.url)
    print(f"Thanks page status: {response2.status_code}")
    content = response2.content.decode()
    print(f"Reference in page: {'BS-' in content}")

print()
print("=== OBJETS CREES EN BASE ===")
contacts = ContactMessage.objects.filter(email='abdoulaye208.mac@gmail.com').order_by('-created_at')[:2]
for c in contacts:
    print(f"Contact: {c.reference} - {c.name} - {c.service} - {c.created_at}")

apps = Application.objects.filter(email='abdoulaye208.mac@gmail.com').order_by('-created_at')[:2]
for a in apps:
    print(f"Application: {a.reference} - {a.name} - {a.job} - {a.created_at}")