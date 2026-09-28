"""Vues contact/devis BS GROUP — logique DIGI-AGENCY + sauvegarde DB + ref unique."""
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from core.seo import seo_for
from core.utils import sender_address
from .models import ContactMessage, QuoteRequest, NewsletterSubscriber


def _noindex(resp):
    resp['X-Robots-Tag'] = 'noindex, nofollow'
    return resp


def contact(request):
    from services.models import Service
    from main.models import SiteSettings
    services = Service.objects.all()
    site_settings = SiteSettings.load()
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        service_slug = (request.POST.get('service') or request.POST.get('subject') or '').strip()
        message = (request.POST.get('message') or '').strip()
        if all([name, email, message]):
            label = service_slug
            try:
                svc = Service.objects.get(slug=service_slug)
                label = svc.title
            except Exception:
                pass
            obj = ContactMessage.objects.create(
                name=name, email=email, phone=phone, service=label, message=message,
            )
            date = timezone.now().strftime('%d/%m/%Y')
            # 1. Confirmation visiteur (HTML comme DIGI)
            html_confirm = render_to_string('email/mail-contact-confirm.html', {
                'prenom': name.split()[0], 'nom': name, 'email': email,
                'telephone': phone, 'service': label or '—',
                'reference': obj.reference, 'date': date,
                'site_settings': site_settings,
            })
            send_mail(f'Demande reçue — Réf. {obj.reference}', '', sender_address(),
                      [email], html_message=html_confirm, fail_silently=True)
            # 2. Notification équipe → même adresse que devis (CONTACT_EMAIL)
            html_team = render_to_string('email/mail-contact-team.html', {
                'nom': name, 'email': email, 'telephone': phone,
                'service': label or '—', 'message': message,
                'reference': obj.reference,
                'date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'site_settings': site_settings,
            })
            send_mail(f'Nouvelle demande {obj.reference} — {label}', '', sender_address(),
                      [getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
                      html_message=html_team, fail_silently=True)
            return redirect('contact:thanks_detail', reference=obj.reference)
    return render(request, 'contact/contact.html', {
        **seo_for(request, title=_('Contact')),
        'services': services, 'site_settings': site_settings,
    })


def quote(request):
    from services.models import Service
    from main.models import SiteSettings
    site_settings = SiteSettings.load()
    if request.method == 'POST':
        # Champs wizard (noms qf-* ou directs) + fallback classique
        def val(*keys):
            for k in keys:
                v = (request.POST.get(k) or '').strip()
                if v:
                    return v
            return ''
        name = val('name', 'qf-name')
        email = val('email', 'qf-email')
        phone = val('phone', 'qf-phone')
        project_type = val('projectType', 'subject', 'service')
        location = val('location', 'qf-location')
        size = val('size', 'qf-size')
        budget = val('budget', 'qf-budget')
        timeline = val('timeline', 'qf-timeline')
        detail = val('message', 'qf-description', 'description')
        if all([name, email, phone, detail]):
            subject = project_type or 'Demande de devis'
            # Message enrichi avec les détails wizard pour l'équipe
            parts = [f'Projet : {project_type or "—"}']
            if location:
                parts.append(f'Localisation : {location}')
            if size:
                parts.append(f'Surface : {size}')
            if budget:
                parts.append(f'Budget : {budget}')
            if timeline:
                parts.append(f'Délai : {timeline}')
            parts.append('')
            parts.append(detail)
            full_message = '\n'.join(parts)
            obj = QuoteRequest.objects.create(
                name=name, email=email, phone=phone, subject=subject, message=full_message,
            )
            date = timezone.now().strftime('%d/%m/%Y')
            html_confirm = render_to_string('email/mail-quote-confirm.html', {
                'prenom': name.split()[0], 'nom': name, 'email': email,
                'telephone': phone, 'subject': subject,
                'reference': obj.reference, 'date': date,
                'site_settings': site_settings,
            })
            send_mail(f'Devis reçu — Réf. {obj.reference}', '', sender_address(),
                      [email], html_message=html_confirm, fail_silently=True)
            # Même adresse que contact (CONTACT_EMAIL) comme demandé
            html_team = render_to_string('email/mail-quote-team.html', {
                'nom': name, 'email': email, 'telephone': phone,
                'subject': subject, 'message': full_message,
                'location': location, 'size': size, 'budget': budget, 'timeline': timeline,
                'reference': obj.reference,
                'date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'site_settings': site_settings,
            })
            send_mail(f'Nouveau devis {obj.reference} — {subject}', '', sender_address(),
                      [getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
                      html_message=html_team, fail_silently=True)
            return redirect('contact:thank_devis_detail', reference=obj.reference)
    return render(request, 'contact/quote.html', {
        **seo_for(request, title=_('Request a Quote')),
        'services': Service.objects.all(),
        'site_settings': site_settings,
    })


def thanks(request, reference=None):
    """thanks/<reference>/ — contact ou candidature. thanks/ seul = page générique (compat)."""
    obj, kind = None, 'general'
    if reference:
        obj = ContactMessage.objects.filter(reference=reference).first()
        if obj:
            kind = 'contact'
        else:
            from careers.models import Application
            obj = Application.objects.filter(reference=reference).select_related('job').first()
            if obj:
                kind = 'application'
        if obj is None:
            from django.http import Http404
            raise Http404('Référence inconnue')
    ctx = {
        **seo_for(request, title=_('Message Sent')),
        'page_robots': 'noindex, nofollow',
        'reference': reference or '',
        'submission': obj, 'submission_kind': kind,
    }
    return _noindex(render(request, 'contact/thanks.html', ctx))


def thank_devis(request, reference=None):
    """thank-devis/<reference>/ — devis uniquement."""
    obj = None
    if reference:
        obj = get_object_or_404(QuoteRequest, reference=reference)
    ctx = {
        **seo_for(request, title=_('Quote Received')),
        'page_robots': 'noindex, nofollow',
        'reference': reference or '',
        'submission': obj, 'submission_kind': 'quote',
    }
    return _noindex(render(request, 'contact/thank-devis.html', ctx))


def newsletter(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
    redirect_to = request.META.get('HTTP_REFERER', '/')
    return redirect(redirect_to)
