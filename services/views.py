"""Vues services BS GROUP — dynamique par slug, design intact."""
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from core.seo import seo_for
from .models import Service
from team.models import Testimonial


def services(request):
    return render(request, 'services/services.html', {
        **seo_for(request, title=_('Services')),
        'services': Service.objects.all(),
        'testimonials': Testimonial.objects.all(),
    })


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    others = Service.objects.exclude(pk=service.pk)[:3]
    return render(request, 'services/service-detail.html', {
        **seo_for(request, obj=service),
        'service': service,
        'services': Service.objects.all(),
        'other_services': others,
        'selected_service': service.slug,
    })
