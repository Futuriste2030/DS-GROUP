#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from services.models import Service

# Service SANS champs SEO (fallback automatique)
s = Service.objects.create(
    title_fr='Rénovation complète',
    title_en='Full Renovation',
    title_ar='تجديد كامل',
    slug='renovation-complete-test-seo',
    excerpt_fr='Rénovation clé en main',
    excerpt_en='Turnkey renovation',
    excerpt_ar='تجديد شامل',
)

print('=== SANS CHAMPS SEO (FALLBACK) ===')
print(f'title_fr: {s.title_fr}')
print(f'meta_title_fr: "{s.meta_title_fr}" (vide)')
print(f'meta_description_fr: "{s.meta_description_fr}" (vide)')
print(f'og_title_fr: "{s.og_title_fr}" (vide)')
print()
print('=== MÉTHODES FALLBACK ===')
print(f'get_meta_title(): {s.get_meta_title()}')
print(f'get_meta_description(): {s.get_meta_description()}')
print(f'get_og_title(): {s.get_og_title()}')
print(f'get_og_description(): {s.get_og_description()}')