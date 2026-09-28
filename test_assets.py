#!/usr/bin/env python
"""Test que les assets locaux sont bien référencés"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from django.test import Client

client = Client()
response = client.get('/')

print(f"Status: {response.status_code}")
content = response.content.decode()

checks = [
    ('tailwind.css', 'tailwind.css' in content),
    ('lucide-loader.js', 'lucide-loader.js' in content),
    ('fonts.css', 'fonts.css' in content),
    ('style.css', 'style.css' in content),
    ('charte-graphique.css', 'charte-graphique.css' in content),
    ('CDN tailwindcss.com', 'cdn.tailwindcss.com' not in content),
    ('CDN unpkg.com/lucide', 'unpkg.com/lucide' not in content),
]

print("\nVérifications assets:")
for name, result in checks:
    status = "OK" if result else "MANQUANT"
    print(f"  {status}: {name}")

# Vérifier que les fichiers existent
import os
base = 'static'
files = [
    'css/tailwind.css',
    'css/fonts.css',
    'css/style.css',
    'css/charte-graphique.css',
    'js/lucide-loader.js',
    'icons/lucide/sparkles.svg',
    'icons/lucide/chevron-right.svg',
    'icons/lucide/arrow-right.svg',
    'icons/lucide/home.svg',
    'icons/lucide/building-2.svg',
]

print("\nFichiers statiques:")
for f in files:
    exists = os.path.exists(os.path.join(base, f))
    status = "OK" if exists else "MANQUANT"
    print(f"  {status}: {f}")