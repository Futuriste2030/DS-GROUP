#!/usr/bin/env python
"""Test conversion automatique WebP à l'upload"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image
import io

# Créer une image de test (JPEG 2000x1500)
img = Image.new('RGB', (2000, 1500), color='red')
buffer = io.BytesIO()
img.save(buffer, format='JPEG', quality=90)
buffer.seek(0)
content = buffer.getvalue()

test_image = SimpleUploadedFile(
    name='test-photo.jpg',
    content=content,
    content_type='image/jpeg'
)

print(f"Image originale: {test_image.name} ({len(content)} bytes)")

# Test via modèle Service (a un champ image)
from services.models import Service

service = Service.objects.create(
    title_fr='Test WebP',
    title_en='Test WebP',
    title_ar='اختبار WebP',
    slug='test-webp-upload',
    excerpt_fr='Test conversion WebP',
    excerpt_en='Test WebP conversion',
    excerpt_ar='تحويل WebP',
    image=test_image,
)

print(f"Image sauvegardée: {service.image.name}")
print(f"URL: {service.image.url}")

# Vérifier le fichier sur disque
from django.conf import settings
filepath = os.path.join(settings.MEDIA_ROOT, service.image.name)
if os.path.exists(filepath):
    size = os.path.getsize(filepath)
    print(f"Fichier sur disque: {filepath} ({size} bytes)")

    # Vérifier que c'est du WebP
    with Image.open(filepath) as im:
        print(f"Format détecté: {im.format}")
        print(f"Dimensions: {im.width}x{im.height}")
        print(f"Mode: {im.mode}")

    # Nettoyer
    service.delete()
    if os.path.exists(filepath):
        os.remove(filepath)
else:
    print("Fichier non trouvé sur disque")

print("\n✅ Test terminé")