from django.db import models
from django.utils.translation import gettext_lazy as _


class SEOMixin(models.Model):
    meta_title = models.CharField(max_length=60, blank=True, help_text=_('Override the default title tag (max 60 chars).'))
    meta_description = models.TextField(max_length=160, blank=True, help_text=_('Meta description (max 160 chars).'))
    meta_keywords = models.CharField(max_length=255, blank=True, help_text=_('Comma-separated keywords.'))
    og_title = models.CharField(max_length=60, blank=True)
    og_description = models.TextField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True)
    twitter_card = models.CharField(max_length=20, choices=[('summary', 'Summary'), ('summary_large_image', 'Summary Large Image')], default='summary_large_image', blank=True)
    canonical_url = models.URLField(blank=True)
    noindex = models.BooleanField(default=False)
    nofollow = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_meta_title(self):
        return self.meta_title or getattr(self, 'title', '') or getattr(self, 'name', '')

    def get_meta_description(self):
        return self.meta_description or getattr(self, 'excerpt', '') or getattr(self, 'description', '') or ''

    def get_og_title(self):
        return self.og_title or self.get_meta_title()

    def get_og_description(self):
        return self.og_description or self.get_meta_description()

    def get_og_image(self):
        if self.og_image:
            return self.og_image.url
        img = getattr(self, 'image', None)
        return img.url if img else ''
