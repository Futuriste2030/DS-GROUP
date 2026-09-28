from main.models import SiteSettings
from services.models import Service


def get_site_settings(request):
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None
    try:
        services = Service.objects.all()
    except Exception:
        services = []
    return {
        'site_settings': settings_obj,
        'services': services,
        'canonical_url': request.build_absolute_uri(request.path),
    }
