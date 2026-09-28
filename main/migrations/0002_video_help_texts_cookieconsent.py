# Vidéo admin (help_texts) + consentements cookies RGPD (parité DIGI-AGENCY).
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='about_video_url',
            field=models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct. Vide = vidéo de démo.'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='about_video_cover',
            field=models.ImageField(blank=True, help_text='Image derrière le bouton play. Vide = About image 1.', upload_to='about/video/'),
        ),
        migrations.CreateModel(
            name='CookieConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=64)),
                ('essential', models.BooleanField(default=True, help_text='Toujours vrai — requis pour le fonctionnement du site')),
                ('statistics', models.BooleanField(default=False, help_text='Cookies analytics & performance')),
                ('marketing', models.BooleanField(default=False, help_text='Cookies publicitaires & ciblage')),
                ('policy_version', models.CharField(default='1.0', max_length=20)),
                ('ip_hash', models.CharField(blank=True, help_text='SHA256 de l’IP client (preuve, aucune IP brute stockée)', max_length=64)),
                ('user_agent', models.CharField(blank=True, max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, help_text='Compte lié quand le visiteur est authentifié.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cookie_consents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cookie Consent',
                'verbose_name_plural': 'Cookie Consents',
            },
        ),
        migrations.CreateModel(
            name='CookieConsentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(default='save', help_text='accept_all / reject_all / save_prefs', max_length=20)),
                ('statistics', models.BooleanField(default=False)),
                ('marketing', models.BooleanField(default=False)),
                ('policy_version', models.CharField(default='1.0', max_length=20)),
                ('ip_hash', models.CharField(blank=True, max_length=64)),
                ('user_agent', models.CharField(blank=True, max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='main.cookieconsent')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Cookie Consent Log',
                'verbose_name_plural': 'Cookie Consent Logs',
            },
        ),
    ]
