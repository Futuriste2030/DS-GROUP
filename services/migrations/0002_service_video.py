# Bannière vidéo Service (parité DIGI-AGENCY).
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='video_cover',
            field=models.ImageField(blank=True, upload_to='services/video/'),
        ),
        migrations.AddField(
            model_name='service',
            name='video_cover_alt',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='service',
            name='video_cover_alt_ar',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='video_cover_alt_en',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='video_cover_alt_fr',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='video_url',
            field=models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct.'),
        ),
    ]
