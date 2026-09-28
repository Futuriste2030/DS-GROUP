from django.db import models
from django.utils.text import slugify
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class Project(SEOMixin, WebPConversionMixin, models.Model):
    webp_fields = ['image', 'image_1', 'image_2', 'testimonial_avatar', 'video_cover']
    webp_max_width = 1920
    webp_quality = 82

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=100, blank=True, default='Commercial Construction')
    location = models.CharField(max_length=200, blank=True, default='New York, USA')
    area = models.CharField(max_length=100, blank=True, default='18.000 Square meters')
    duration = models.CharField(max_length=100, blank=True, default='5Y, 3M')
    period = models.CharField(max_length=50, blank=True, default='2022-2025')
    image = models.ImageField(upload_to='projects/', blank=True)
    excerpt = models.TextField(blank=True)
    intro = models.TextField(blank=True)
    description = models.TextField(blank=True)
    challenge_title = models.CharField(max_length=200, default='The Challenge')
    challenge = models.TextField(blank=True)
    solution_title = models.CharField(max_length=200, default='The Solution')
    solution = models.TextField(blank=True)
    image_1 = models.ImageField(upload_to='projects/', blank=True)
    image_1_alt = models.CharField(max_length=200, blank=True)
    image_2 = models.ImageField(upload_to='projects/', blank=True)
    image_2_alt = models.CharField(max_length=200, blank=True)
    scope_title = models.CharField(max_length=200, blank=True, default='What We Delivered')
    scope_description = models.TextField(blank=True)
    result_title = models.CharField(max_length=200, blank=True, default='A Landmark Delivered On Time')
    result = models.TextField(blank=True)
    testimonial_title = models.CharField(max_length=200, blank=True, default='Top-Notch Service!')
    testimonial_text = models.TextField(blank=True)
    testimonial_name = models.CharField(max_length=200, blank=True)
    testimonial_role = models.CharField(max_length=200, blank=True, default='Happy Client')
    testimonial_avatar = models.ImageField(upload_to='projects/testimonials/', blank=True)

    # Bannière vidéo (même logique que DIGI-AGENCY)
    video_cover = models.ImageField(upload_to='projects/video/', blank=True)
    video_cover_alt = models.CharField(max_length=200, blank=True)
    video_url = models.URLField(blank=True, help_text='URL embed YouTube (…/embed/…) ou fichier MP4 direct.')
    order = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_fr or self.title_en or self.title or 'project')
            slug, i = base or 'project', 1
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProjectPoint(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='points')
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class ProjectStep(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='steps')
    number = models.CharField(max_length=10, default='01')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.number} — {self.title}'