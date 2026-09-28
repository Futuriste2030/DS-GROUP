"""Vues projets BS GROUP — dynamique par slug, design intact."""
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from core.seo import seo_for
from .models import Project


def projets(request):
    from team.models import Testimonial
    from main.models import ProcessStep
    return render(request, 'projects/projets.html', {
        **seo_for(request, title=_('Projects')),
        'projects': Project.objects.all(),
        'testimonials': Testimonial.objects.all(),
        'processes': ProcessStep.objects.all(),
    })


def projet_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    others = Project.objects.exclude(pk=project.pk)[:2]
    return render(request, 'projects/projet-detail.html', {
        **seo_for(request, obj=project),
        'project': project,
        'other_projects': others,
    })
