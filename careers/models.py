from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class CareerPage(WebPConversionMixin, models.Model):
    webp_fields = ['video_banner_image']
    webp_max_width = 1920
    webp_quality = 82

    hero_title = models.CharField(max_length=300, default='Join Our Team')
    hero_subtitle = models.CharField(max_length=200, default='Careers')
    openings_title = models.CharField(max_length=300, default='Current Openings')
    openings_subtitle = models.CharField(max_length=200, default='Job Opening')
    video_url = models.URLField(blank=True)
    video_banner_image = models.ImageField(upload_to='careers/banner/', blank=True)

    class Meta:
        verbose_name = 'Career Page'
        verbose_name_plural = 'Career Page'

    def __str__(self):
        return 'Career Page Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Perk(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='star')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class JobOpening(SEOMixin, models.Model):
    JOB_TYPES = [('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship')]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True, default='Engineering')
    location = models.CharField(max_length=200, blank=True, default='New York, NY')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    experience = models.CharField(max_length=100, blank=True, default='5+ Years')
    salary = models.CharField(max_length=100, blank=True, default='$95k – $120k / year')
    deadline = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True, help_text='Un item par ligne')
    requirements = models.TextField(blank=True, help_text='Un item par ligne')
    nice_to_have = models.TextField(blank=True, help_text='Un item par ligne')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_fr or self.title_en or self.title or 'offre')
            slug, i = base or 'offre', 1
            while JobOpening.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def responsibilities_list(self):
        return [r.strip() for r in (self.responsibilities or '').splitlines() if r.strip()]

    def requirements_list(self):
        return [r.strip() for r in (self.requirements or '').splitlines() if r.strip()]

    def nice_list(self):
        return [r.strip() for r in (self.nice_to_have or '').splitlines() if r.strip()]


class Application(models.Model):
    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name='applications')
    reference = models.CharField(max_length=200, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    resume = models.FileField(upload_to='careers/resumes/')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} — {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().strftime('%Y')
            base = f"BS-{year}-{self.job.title.upper().replace(' ', '-')[:20]}-{self.full_name.upper().replace(' ', '-')[:20]}"
            ref, i = base, 1
            while Application.objects.filter(reference=ref).exists():
                ref = f'{base}-{i}'
                i += 1
            self.reference = ref
        super().save(*args, **kwargs)