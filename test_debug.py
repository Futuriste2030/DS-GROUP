#!/usr/bin/env python
"""Debug WebP conversion - check file type"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bsgroup.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from services.models import Service
from core.fields import WebPImageField
from PIL import Image
import io

# Patch pre_save pour debug
original_pre_save = WebPImageField.pre_save

def debug_pre_save(self, model_instance, add):
    file = super(WebPImageField, self).pre_save(model_instance, add)
    print(f'pre_save - type: {type(file)}, isinstance UploadedFile: {isinstance(file, UploadedFile) if file else "None"}')
    return file

WebPImageField.pre_save = debug_pre_save

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

service = Service.objects.create(
    title_fr='Test WebP',
    title_en='Test WebP',
    title_ar='Test',
    slug='test-webp-debug-type',
    excerpt_fr='Test',
    excerpt_en='Test',
    excerpt_ar='Test',
    image=test_image,
)

print(f'Après: {service.image.name}')

filepath = service.image.path
if os.path.exists(filepath):
    with Image.open(filepath) as im:
        print(f'Format: {im.format}, Dim: {im.width}x{im.height}')

service.delete()
if os.path.exists(filepath):
    os.remove(filepath)