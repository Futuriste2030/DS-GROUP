from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from services.models import Service
from projects.models import Project
from blog.models import Post
from team.models import TeamMember
from careers.models import JobOpening

# Domaine canonique unique — même logique que DIGI-AGENCY :
# le sitemap liste toujours https://<CANONICAL_DOMAIN>/...
# quel que soit l'Host de la requête, pour éviter le contenu dupliqué.
CANONICAL_DOMAIN = getattr(settings, 'CANONICAL_DOMAIN', 'bsgroup.ml')


class CanonicalSitemap(Sitemap):
    """Base : HTTPS + domaine canonique + une URL par langue.

    - ``protocol = 'https'`` : jamais de http:// même derrière un proxy.
    - ``get_domain`` forcé : sitemap identique sur apex et www.
    - ``i18n = True`` : Django émet une <url> par langue active
      (fr sans préfixe, /en/, /ar/), au lieu du seul français.
    - En DEBUG local on garde l'Host de la requête pour valider en local.
    """

    protocol = 'https'
    i18n = True

    def get_domain(self, site=None):
        if settings.DEBUG:
            return super().get_domain(site)
        return CANONICAL_DOMAIN

    def get_protocol(self, protocol=None):
        return 'https'


class StaticViewSitemap(CanonicalSitemap):
    priorities = {
        'main:index': 1.0,
        'services:services': 0.9,
        'projects:projets': 0.9,
        'blog:blogs': 0.9,
        'careers:careers': 0.8,
        'main:about': 0.8,
        'contact:contact': 0.8,
        'contact:devis': 0.8,
        'team:team': 0.6,
        'team:testimonials': 0.5,
        'main:faqs': 0.6,
        'main:legales': 0.3,
        'main:privacy': 0.3,
        'main:cgu': 0.3,
        'main:cookies': 0.3,
    }
    changefreq = 'weekly'

    def items(self):
        return list(self.priorities)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.priorities.get(item, 0.5)


class ServiceSitemap(CanonicalSitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        # Pas de noindex dans le sitemap : Google rejette les sitemaps
        # qui listent des URLs non indexables.
        return Service.objects.filter(noindex=False)

    def location(self, obj):
        return reverse('services:service-detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created


class ProjectSitemap(CanonicalSitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(noindex=False)

    def location(self, obj):
        return reverse('projects:projet-detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created


class PostSitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Post.objects.filter(noindex=False)

    def location(self, obj):
        return reverse('blog:blog-detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.published


class TeamMemberSitemap(CanonicalSitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return TeamMember.objects.filter(noindex=False)

    def location(self, obj):
        return reverse('team:team-detail', kwargs={'slug': obj.slug})


class JobOpeningSitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return JobOpening.objects.filter(is_active=True, noindex=False)

    def location(self, obj):
        return reverse('careers:career-detail', kwargs={'slug': obj.slug})


sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'projects': ProjectSitemap,
    'posts': PostSitemap,
    'team': TeamMemberSitemap,
    'jobs': JobOpeningSitemap,
}
