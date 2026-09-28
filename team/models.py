from django.db import models
from django.utils.text import slugify
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class TeamMember(SEOMixin, WebPConversionMixin, models.Model):
    webp_fields = ['image']
    webp_max_width = 800
    webp_quality = 82

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    role = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True, default='Leadership')
    bio = models.TextField(blank=True)
    bio_2 = models.TextField(blank=True)
    quote = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text='Une compétence par ligne : Nom | pourcentage')
    experience_years = models.PositiveIntegerField(default=10)
    projects_count = models.PositiveIntegerField(default=100)
    people_led = models.PositiveIntegerField(default=50)
    awards_count = models.PositiveIntegerField(default=5)
    image = models.ImageField(upload_to='team/', blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    office = models.CharField(max_length=200, blank=True, default='HQ · New York, NY')
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            i = 1
            while TeamMember.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def parse_skills(self):
        out = []
        for line in (self.skills or '').strip().splitlines():
            line = line.strip()
            if '|' in line:
                n, p = line.split('|', 1)
                try:
                    out.append((n.strip(), int(p.strip())))
                except ValueError:
                    pass
            elif line:
                out.append((line, 80))
        return out


class TeamExperience(models.Model):
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='experiences')
    period = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    current = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.period} — {self.title}'


class TeamCertification(models.Model):
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Testimonial(WebPConversionMixin, models.Model):
    webp_fields = ['client_avatar']
    webp_max_width = 400
    webp_quality = 82

    client_name = models.CharField(max_length=200)
    client_role = models.CharField(max_length=200, blank=True)
    client_avatar = models.ImageField(upload_to='testimonials/', blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    title = models.CharField(max_length=200, blank=True, default='Top-Notch Service!')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.client_name} — {self.rating}'