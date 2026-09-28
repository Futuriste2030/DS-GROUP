from django.db import models
from django.utils.text import slugify
from core.models import SEOMixin
from core.mixins import WebPConversionMixin


class Post(SEOMixin, WebPConversionMixin, models.Model):
    webp_fields = ['author_avatar', 'image']
    webp_max_width = 1920
    webp_quality = 82

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    author_name = models.CharField(max_length=200, default='BS GROUP')
    author_avatar = models.ImageField(upload_to='blog/avatars/', blank=True)
    author_bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/', blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Contenu HTML de l'article")
    reading_time = models.CharField(max_length=50, default='5 min Read')
    published = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-published']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_fr or self.title_en or self.title or 'article')
            slug, i = base or 'article', 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]