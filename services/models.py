from django.db import models
from django.utils.text import slugify
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class Service(SEOMixin, WebPConversionMixin, models.Model):
    webp_fields = ['image', 'image_1', 'image_2', 'video_cover']
    webp_max_width = 1920
    webp_quality = 82

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/', blank=True)
    category = models.CharField(max_length=100, blank=True, default='Residential')
    timeline = models.CharField(max_length=100, blank=True, default='8 – 24 Months')
    team_size = models.CharField(max_length=100, blank=True, default='10 – 45 Specialists')
    warranty = models.CharField(max_length=100, blank=True, default='10 Years Structural')
    icon = models.CharField(max_length=50, blank=True, default='building')

    intro = models.TextField(blank=True)
    approach_title = models.CharField(max_length=200, blank=True, default='Our Approach')
    approach = models.TextField(blank=True)

    includes_title = models.CharField(max_length=200, default="What's Included")
    includes_description = models.TextField(blank=True)
    image_1 = models.ImageField(upload_to='services/', blank=True)
    image_1_alt = models.CharField(max_length=200, blank=True)
    image_2 = models.ImageField(upload_to='services/', blank=True)
    image_2_alt = models.CharField(max_length=200, blank=True)

    benefits_title = models.CharField(max_length=200, blank=True, default='Benefits That Set Us Apart')
    benefits_description = models.TextField(blank=True)

    # Bannière vidéo (même logique que DIGI-AGENCY)
    video_cover = models.ImageField(upload_to='services/video/', blank=True)
    video_cover_alt = models.CharField(max_length=200, blank=True)
    video_url = models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct.')

    process_title = models.CharField(max_length=200, blank=True, default='How We Build')
    process_description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_fr or self.title_en or self.title or 'service')
            slug, i = base or 'service', 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ServiceBenefit(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='benefits_list')
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='shield-check')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ServiceStep(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='steps')
    number = models.CharField(max_length=10, default='01')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.number} — {self.title}'