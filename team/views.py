"""Vues équipe BS GROUP — dynamique par slug, design intact."""
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from core.seo import seo_for
from .models import TeamMember, Testimonial


def team(request):
    return render(request, 'team/team.html', {
        **seo_for(request, title=_('Team')),
        'members': TeamMember.objects.all(),
    })


def team_detail(request, slug):
    member = get_object_or_404(TeamMember, slug=slug)
    others = TeamMember.objects.exclude(pk=member.pk)[:3]
    return render(request, 'team/team-detail.html', {
        **seo_for(request, obj=member),
        'member': member,
        'other_members': others,
        'members': TeamMember.objects.all(),
    })


def testimonials(request):
    return render(request, 'team/testimonials.html', {
        **seo_for(request, title=_('Testimonials')),
        'testimonials': Testimonial.objects.all(),
        'members': TeamMember.objects.all()[:3],
    })
