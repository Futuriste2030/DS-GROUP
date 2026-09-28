"""
Mixin pour conversion automatique WebP — à ajouter sur les modèles.
Utilise signal pre_save pour intercepter avant sauvegarde.
"""
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image, ImageOps
import io


class WebPConversionMixin:
    """
    Mixin à hériter sur les modèles ayant des champs WebPImageField.
    Convertit automatiquement les images en WebP avant sauvegarde.
    """
    # Liste des noms de champs à convertir (à définir dans le modèle enfant)
    webp_fields = []
    webp_max_width = 1920
    webp_quality = 82

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._convert_webp_images()
        super().save(*args, **kwargs)

    def _convert_webp_images(self):
        from django.core.files.base import ContentFile
        import os

        for field_name in self.webp_fields:
            field_file = getattr(self, field_name, None)
            if field_file and hasattr(field_file, 'file') and field_file.file:
                # Vérifier si c'est un nouveau fichier (pas encore en base)
                # ou si le fichier a changé
                if getattr(field_file, '_committed', False):
                    continue  # Déjà sauvegardé

                try:
                    file_obj = field_file.file
                    # Revenir au début si c'est un fichier ouvert
                    if hasattr(file_obj, 'seek'):
                        file_obj.seek(0)

                    # Ouvrir et convertir
                    image = Image.open(file_obj)
                    image = ImageOps.exif_transpose(image)

                    if image.width > self.webp_max_width:
                        ratio = self.webp_max_width / image.width
                        new_height = int(image.height * ratio)
                        image = image.resize((self.webp_max_width, new_height), Image.Resampling.LANCZOS)

                    output = io.BytesIO()
                    if image.mode in ('RGBA', 'LA', 'P'):
                        image = image.convert('RGBA')
                    else:
                        image = image.convert('RGB')

                    image.save(output, format='WEBP', quality=self.webp_quality, method=6)
                    output.seek(0)

                    # Remplacer le fichier
                    old_name = getattr(field_file, 'name', 'image')
                    name, _ = os.path.splitext(old_name)
                    new_file = ContentFile(output.getvalue(), name=f"{name}.webp")

                    # Sauvegarder sans déclencher de boucle infinie
                    field_file.save(new_file.name, new_file, save=False)

                except Exception:
                    pass  # Garder l'original en cas d'erreur


# Fonction utilitaire pour connecter le signal automatiquement
def register_webp_conversion(model_class):
    """Enregistre la conversion WebP pour un modèle"""
    @receiver(pre_save, sender=model_class)
    def convert_images(sender, instance, **kwargs):
        if hasattr(instance, '_convert_webp_images'):
            instance._convert_webp_images()
    return convert_images