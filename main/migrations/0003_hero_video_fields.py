# Champs vidéo dédiés au hero (parité avec about_video_*).
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_video_help_texts_cookieconsent'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='hero_video_cover',
            field=models.ImageField(blank=True, help_text='Image du cadre hero derrière le bouton play. Vide = Hero image 1.', upload_to='hero/video/'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='hero_video_url',
            field=models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct pour le bouton play du hero. Vide = vidéo About.'),
        ),
    ]
