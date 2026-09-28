"""
Champs d'image optimisés — conversion automatique WebP + compression.
Override save_form_data pour intercepter l'UploadedFile brut avant stockage.
"""
from django.db import models
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps
import io


class WebPImageField(models.ImageField):
    """
    ImageField qui convertit automatiquement en WebP à l'upload.
    - Redimensionne si > max_width (défaut 1920px)
    - Convertit en WebP (qualité 82)
    - Préserve EXIF orientation
    - Change l'extension en .webp
    """
    def __init__(self, *args, max_width=1920, quality=82, **kwargs):
        self.max_width = max_width
        self.quality = quality
        super().__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        """Intercepte l'UploadedFile brut avant stockage Django"""
        if data and isinstance(data, UploadedFile):
            try:
                # Ouvrir et corriger orientation EXIF
                image = Image.open(data)
                image = ImageOps.exif_transpose(image)

                # Redimensionner si nécessaire
                if image.width > self.max_width:
                    ratio = self.max_width / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((self.max_width, new_height), Image.Resampling.LANCZOS)

                # Convertir en WebP
                output = io.BytesIO()
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')

                image.save(output, format='WEBP', quality=self.quality, method=6)
                output.seek(0)

                # Créer nouveau fichier WebP
                import os
                name, _ = os.path.splitext(data.name)
                from django.core.files.base import ContentFile
                new_file = ContentFile(output.getvalue(), name=f"{name}.webp")
                # Appeler le parent avec le fichier converti
                return super().save_form_data(instance, new_file)
            except Exception:
                pass  # En cas d'erreur, laisser le parent gérer l'original
        return super().save_form_data(instance, data)