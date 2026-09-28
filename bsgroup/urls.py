"""URL configuration for bsgroup project — même logique i18n que DIGI-AGENCY."""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve as static_serve
from django.urls import re_path

from core.sitemaps import sitemaps
from main.views import not_found, server_error

handler404 = not_found
handler500 = server_error


def sitemap_view(request):
    """Sitemap sans X-Robots-Tag: noindex — même logique que DIGI-AGENCY.

    Certains panels / reverse proxys ajoutent `X-Robots-Tag: noindex`
    sur les .xml, ce qui fait rejeter le sitemap par la Search Console.
    On force ici un en-tête autorisant l'exploration.
    """
    response = django_sitemap(request, sitemaps=sitemaps)
    response['X-Robots-Tag'] = 'index, follow'
    response.headers.pop('Content-Security-Policy', None)
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('chatbot.urls')),
    path('api/', include('main.api_urls')),
    path('sitemap.xml', sitemap_view, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

urlpatterns += i18n_patterns(
    path('', include('main.urls')),
    path('', include('services.urls')),
    path('', include('team.urls')),
    path('', include('projects.urls')),
    path('', include('blog.urls')),
    path('', include('careers.urls')),
    path('', include('contact.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]
