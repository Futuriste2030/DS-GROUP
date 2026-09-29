"""Vues carrières BS GROUP — même logique que DIGI (liste + apply + emails)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from core.seo import seo_for
from core.utils import sender_address
from .models import CareerPage, Perk, HiringStep, JobOpening, Application


def careers(request):
    from team.models import TeamMember
    page = CareerPage.load()
    jobs = JobOpening.objects.filter(is_active=True)
    return render(request, 'careers/careers.html', {
        **seo_for(request, title=_('Careers')),
        'page': page,
        'perks': Perk.objects.all(),
        'hiring_steps': HiringStep.objects.all(),
        'jobs': jobs,
        'team_count': TeamMember.objects.count(),
    })


def career_detail(request, slug):
    job = get_object_or_404(JobOpening, slug=slug, is_active=True)
    others = JobOpening.objects.filter(is_active=True).exclude(pk=job.pk)[:3]
    return render(request, 'careers/career-detail.html', {
        **seo_for(request, obj=job),
        'job': job,
        'other_jobs': others,
        'jobs': JobOpening.objects.filter(is_active=True),
    })


def career_apply(request):
    if request.method != 'POST':
        return redirect('careers:careers')
    job_id = request.POST.get('job_id') or request.POST.get('position')
    full_name = (request.POST.get('name') or request.POST.get('fullName') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    message = (request.POST.get('message') or request.POST.get('coverLetter') or '').strip()
    resume = request.FILES.get('resume') or request.FILES.get('cv') or request.FILES.get('file')
    if not all([job_id, full_name, email, phone, resume]):
        # job_id peut être un slug/titre (select du template)
        job = JobOpening.objects.filter(is_active=True).first()
        if not job:
            return redirect('careers:careers')
    else:
        try:
            job = JobOpening.objects.get(pk=job_id)
        except (JobOpening.DoesNotExist, ValueError):
            job = JobOpening.objects.filter(title__iexact=str(job_id)).first() or JobOpening.objects.filter(slug=str(job_id)).first()
            if not job:
                return redirect('careers:careers')
    app = Application(job=job, full_name=full_name, email=email, phone=phone, message=message, resume=resume)
    app.save()
    from main.models import SiteSettings
    site_settings = SiteSettings.load()
    date = timezone.now().strftime('%d/%m/%Y')
    html_confirm = render_to_string('email/mail-career-confirm.html', {
        'prenom': full_name.split()[0], 'poste': job.title, 'email': email,
        'reference': app.reference, 'documents': resume.name if resume else '—',
        'date': date, 'site_settings': site_settings,
    })
    send_mail(f'Candidature reçue — Réf. {app.reference}', '', sender_address(), [email],
              html_message=html_confirm, fail_silently=True)
    hr = getattr(settings, 'HR_EMAIL', settings.DEFAULT_FROM_EMAIL)
    html_hr = render_to_string('email/mail-rh-career.html', {
        'prenom': full_name.split()[0], 'nom': full_name, 'poste': job.title,
        'email': email, 'telephone': phone, 'reference': app.reference,
        'cv_url': app.resume.url if app.resume else '',
        'message': message or 'Aucun message',
        'date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
        'site_settings': site_settings,
    })
    send_mail(f'Nouvelle candidature {app.reference} — {job.title}', '', sender_address(), [hr],
              html_message=html_hr, fail_silently=True)
    return redirect('contact:thanks_detail', reference=app.reference)


def career_success(request, reference=None):
    from contact.models import ContactMessage
    obj = None
    if reference:
        obj = Application.objects.filter(reference=reference).select_related('job').first()
    return render(request, 'contact/thanks.html', {
        'page_robots': 'noindex, nofollow',
        'reference': reference or '',
        'submission': obj, 'submission_kind': 'application' if obj else 'general',
    })
