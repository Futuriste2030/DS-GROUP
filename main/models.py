from django.db import models
import uuid
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class SiteSettings(SEOMixin, WebPConversionMixin, models.Model):
    webp_fields = ['logo', 'about_video_cover', 'about_image_1', 'about_image_2',
                   'why_image_1', 'why_image_2', 'hero_image_1', 'hero_image_2',
                   'hero_image_3', 'hero_video_cover', 'contact_image']
    webp_max_width = 1920
    webp_quality = 82

    company_name = models.CharField(max_length=200, default='BS GROUP')
    company_short_name = models.CharField(max_length=100, blank=True, default='BS GROUP')
    site_url = models.URLField(default='https://bsgroup.ml')
    logo = models.ImageField(upload_to='site/', blank=True)
    footer_description = models.TextField(default='BS GROUP — Écosystème intégré : échange, finance, infrastructures et commerce.')

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    careers_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    map_query = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    nif = models.CharField(max_length=20, blank=True, verbose_name='NIF')
    rccm = models.CharField(max_length=100, blank=True, verbose_name='RCCM')
    director_name = models.CharField(max_length=200, blank=True)
    hosting_provider = models.CharField(max_length=200, blank=True)
    hosting_address = models.CharField(max_length=500, blank=True)
    hosting_city_country = models.CharField(max_length=200, blank=True, default='Mesa, New Jersey')

    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)

    coming_soon_enabled = models.BooleanField(default=False)
    launch_date = models.DateField(blank=True, null=True)

    about_video_url = models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct. Vide = vidéo de démo.')
    about_video_cover = models.ImageField(upload_to='about/video/', blank=True, help_text='Image derrière le bouton play. Vide = About image 1.')
    about_title = models.CharField(max_length=300, blank=True, default='BS GROUP')
    about_description = models.TextField(blank=True)
    about_description_2 = models.TextField(blank=True)
    about_section_title = models.CharField(max_length=300, blank=True, default='Construire l’avenir avec précision')
    about_section_subtitle = models.CharField(max_length=100, blank=True, default='About Us')
    about_image_1 = models.ImageField(upload_to='about/', blank=True)
    about_image_2 = models.ImageField(upload_to='about/', blank=True)
    vision_title = models.CharField(max_length=200, blank=True, default='Our Vision')
    vision_description = models.TextField(blank=True)
    mission_title = models.CharField(max_length=200, blank=True, default='Our Mission')
    mission_description = models.TextField(blank=True)

    process_title = models.CharField(max_length=300, blank=True, default='How We Build')
    process_description = models.TextField(blank=True)

    why_subtitle = models.CharField(max_length=100, blank=True, default='Why Choose Us')
    why_title = models.CharField(max_length=300, blank=True, default='Why Our Clients Trust Us')
    why_image_1 = models.ImageField(upload_to='why/', blank=True)
    why_image_2 = models.ImageField(upload_to='why/', blank=True)

    hero_badge = models.CharField(max_length=200, blank=True, default='BS GROUP — Bâtir avec excellence')
    hero_title = models.CharField(max_length=400, blank=True, default='Construire l’avenir avec précision')
    hero_description = models.TextField(blank=True)
    hero_image_1 = models.ImageField(upload_to='hero/', blank=True)
    hero_image_2 = models.ImageField(upload_to='hero/', blank=True)
    hero_image_3 = models.ImageField(upload_to='hero/', blank=True)
    hero_video_url = models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct pour le bouton play du hero. Vide = vidéo About.')
    hero_video_cover = models.ImageField(upload_to='hero/video/', blank=True, help_text='Image du cadre hero derrière le bouton play. Vide = Hero image 1.')

    contact_image = models.ImageField(upload_to='contact/', blank=True)
    services_section_title = models.CharField(max_length=300, blank=True, default='Nos expertises construction')

    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    meta_author = models.CharField(max_length=200, blank=True, default='BS GROUP')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def base_url(self):
        return (self.site_url or '').rstrip('/')


class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


class Partner(WebPConversionMixin, models.Model):
    webp_fields = ['logo']
    webp_max_width = 800
    webp_quality = 82

    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/', blank=True)
    website = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Cookie Consent — preuve RGPD des choix visiteurs (même logique que DIGI-AGENCY)
# ---------------------------------------------------------------------------

class CookieConsent(models.Model):
    # ID stable first-party (cookie + localStorage, 13 mois).
    consent_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    # Clé legacy : session Django (peut tourner alors que consent_id reste stable).
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    user = models.ForeignKey(
        'auth.User', blank=True, null=True, on_delete=models.SET_NULL,
        related_name='cookie_consents',
        help_text='Compte lié quand le visiteur est authentifié.',
    )
    essential = models.BooleanField(default=True, help_text='Toujours vrai — requis pour le fonctionnement du site')
    statistics = models.BooleanField(default=False, help_text='Cookies analytics & performance')
    marketing = models.BooleanField(default=False, help_text='Cookies publicitaires & ciblage')
    policy_version = models.CharField(max_length=20, default='1.0')
    ip_hash = models.CharField(max_length=64, blank=True, help_text='SHA256 de l\'IP client (preuve, aucune IP brute stockée)')
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cookie Consent'
        verbose_name_plural = 'Cookie Consents'

    def __str__(self):
        return f'{self.consent_id} — stats={self.statistics} mkt={self.marketing}'


class CookieConsentLog(models.Model):
    """Historique append-only : chaque Accept/Reject/Save crée une ligne, jamais écrasée."""

    consent = models.ForeignKey(CookieConsent, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, default='save', help_text='accept_all / reject_all / save_prefs')
    statistics = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    policy_version = models.CharField(max_length=20, default='1.0')
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cookie Consent Log'
        verbose_name_plural = 'Cookie Consent Logs'

    def __str__(self):
        return f'{self.consent_id} {self.action} @ {self.created_at:%Y-%m-%d %H:%M}'


# ---------------------------------------------------------------------------
# Modèles SEO / Contenu dynamique (utilisés dans admin / templates)
# ---------------------------------------------------------------------------

class SiteStat(models.Model):
    value = models.CharField(max_length=20)
    suffix = models.CharField(max_length=10, blank=True)
    label = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.value}{self.suffix} {self.label}'


class SkillBar(models.Model):
    label = models.CharField(max_length=200)
    percentage = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.label} ({self.percentage}%)'


class ProcessStep(models.Model):
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Step {self.number}: {self.title}'


class Feature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class LegalPage(models.Model):
    PAGE_TYPES = [('legal', 'Mentions Légales'), ('privacy', 'Politique de Confidentialité'), ('cgu', 'CGU'), ('cookies', 'Politique Cookies')]
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    intro = models.TextField(blank=True)
    last_updated = models.DateField(blank=True, null=True)
    version_number = models.CharField(max_length=20, default='1.0')

    def __str__(self):
        return self.get_page_type_display()


class LegalArticle(models.Model):
    page = models.ForeignKey(LegalPage, on_delete=models.CASCADE, related_name='articles')
    number = models.CharField(max_length=10)
    title = models.CharField(max_length=300)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.number}. {self.title}'