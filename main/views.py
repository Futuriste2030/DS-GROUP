"""Vues vitrine BS GROUP — même logique dynamique que DIGI-AGENCY."""
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from core.seo import seo_for

def index(request):
    from services.models import Service
    from projects.models import Project
    from blog.models import Post
    from team.models import TeamMember, Testimonial
    from careers.models import JobOpening
    from main.models import FAQ, SiteStat, ProcessStep, Feature
    testimonials_qs = Testimonial.objects.all()
    return render(request, 'main/index.html', {
        **seo_for(request, title=_('Home'), description=_('BS GROUP — Écosystème intégré : échange, finance, infrastructures et commerce.')),
        'services': Service.objects.all()[:6],
        'projects': Project.objects.all()[:4],
        'posts': Post.objects.all()[:3],
        'team': TeamMember.objects.all()[:3],
        'testimonials': testimonials_qs,
        'testimonials_json': [
            {
                'name': t.client_name,
                'role': t.client_role,
                'avatar': t.client_avatar.url if t.client_avatar else '',
                'rating': float(t.rating),
                'title': t.title,
                'text': t.text,
            }
            for t in testimonials_qs
        ],
        'jobs': JobOpening.objects.filter(is_active=True)[:4],
        'faqs': FAQ.objects.all()[:5],
        'stats': SiteStat.objects.all()[:4],
        'processes': ProcessStep.objects.all(),
        'features': Feature.objects.all()[:4],
    })


def about(request):
    from services.models import Service
    from team.models import TeamMember, Testimonial
    from main.models import SiteStat, SkillBar, ProcessStep, Feature, FAQ, TimelineEvent
    testimonials_qs = Testimonial.objects.all()
    return render(request, 'main/about.html', {
        **seo_for(request, title=_('About Us')),
        'services': Service.objects.all(),
        'stats': SiteStat.objects.all(),
        'skills': SkillBar.objects.all(),
        'processes': ProcessStep.objects.all(),
        'features': Feature.objects.all(),
        'timeline': TimelineEvent.objects.all(),
        'team': TeamMember.objects.all()[:3],
        'testimonials': testimonials_qs,
        'testimonials_json': [
            {
                'name': t.client_name,
                'role': t.client_role,
                'avatar': t.client_avatar.url if t.client_avatar else '',
                'rating': float(t.rating),
                'title': t.title,
                'text': t.text,
            }
            for t in testimonials_qs
        ],
        'faqs': FAQ.objects.all()[:5],
    })


def faqs(request):
    from main.models import FAQ
    return render(request, 'main/faqs.html', {
        **seo_for(request, title=_('FAQ')),
        'faqs': FAQ.objects.all(),
    })


def _legal(request, page_type, template, title):
    from main.models import LegalPage
    try:
        page = LegalPage.objects.prefetch_related('articles').get(page_type=page_type)
    except LegalPage.DoesNotExist:
        page = None
    desc = page.description if page and page.description else title
    return render(request, template, {
        **seo_for(request, title=title, description=desc),
        'legal_page': page,
    })


def cgu(request):
    return _legal(request, 'cgu', 'main/cgu.html', _('Terms'))


def cookies(request):
    return _legal(request, 'cookies', 'main/cookies.html', _('Cookie Policy'))


def legales(request):
    return _legal(request, 'legal', 'main/legales.html', _('Legal Notice'))


def privacy(request):
    return _legal(request, 'privacy', 'main/privacy.html', _('Privacy Policy'))


def coming(request):
    from main.models import SiteSettings
    if request.method == 'POST':
        from contact.models import NotifySubscriber
        email = (request.POST.get('email') or '').strip()
        if email:
            NotifySubscriber.objects.get_or_create(email=email)
            return redirect('main:coming')
    try:
        enabled = SiteSettings.load().coming_soon_enabled
    except Exception:
        enabled = False
    if not enabled and request.method != 'POST':
        return redirect('main:index')
    return render(request, 'main/coming.html', {
        **seo_for(request, title=_('Coming Soon')),
        'page_robots': 'noindex, nofollow',
        'coming_enabled': enabled,
    })


def not_found(request, exception=None):
    response = render(request, 'main/404.html', {'page_robots': 'noindex, nofollow'})
    response.status_code = 404
    return response


def server_error(request):
    response = render(request, 'main/404.html', {'page_robots': 'noindex, nofollow'})
    response.status_code = 500
    return response


def _consent_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _consent_ip_hash(ip):
    import hashlib
    return hashlib.sha256((ip or '').encode()).hexdigest()


def _parse_consent_id(value):
    import uuid as _uuid
    try:
        return _uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None


def cookie_consent(request):
    """GET = état courant (vérité serveur) ; POST = sauvegarde des choix.

    POST JSON : { statistics: bool, marketing: bool, consent_id?: uuid, action?: str }
    Réponse JSON : { status, essential, statistics, marketing, consent_id, has_consented }.
    Le serveur pose aussi le cookie stable `consent_id` (13 mois, Lax).
    Même logique que DIGI-AGENCY.
    """
    from django.conf import settings as _settings
    from django.http import JsonResponse
    import json as _json
    import uuid as _uuid

    cookie_name = getattr(_settings, 'CONSENT_COOKIE_NAME', 'consent_id')
    cookie_age = getattr(_settings, 'CONSENT_COOKIE_AGE', 60 * 60 * 24 * 395)
    policy_version = getattr(_settings, 'COOKIE_POLICY_VERSION', '1.0')

    if request.method == 'GET':
        state = getattr(request, 'cookie_consent', None) or {
            'essential': True, 'statistics': False, 'marketing': False,
            'has_consented': False, 'consent_id': None,
        }
        return JsonResponse({
            'essential': True,
            'statistics': bool(state.get('statistics', False)),
            'marketing': bool(state.get('marketing', False)),
            'has_consented': bool(state.get('has_consented', False)),
            'consent_id': state.get('consent_id'),
            'policy_version': policy_version,
        })

    if request.method != 'POST':
        return JsonResponse({'error': 'GET or POST required'}, status=405)

    try:
        data = _json.loads(request.body or '{}')
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    from .models import CookieConsent, CookieConsentLog

    statistics = bool(data.get('statistics', False))
    marketing = bool(data.get('marketing', False))
    action = str(data.get('action', 'save') or 'save')[:20]

    # Réutilise l'ID stable (body ou cookie), sinon nouveau.
    cid = _parse_consent_id(data.get('consent_id')) or _parse_consent_id(request.COOKIES.get(cookie_name))
    is_new = False
    if cid is None:
        cid = _uuid.uuid4()
        is_new = True

    # Session créée ici seulement — l'utilisateur vient de faire un choix.
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key or ''

    ip_hash = _consent_ip_hash(_consent_client_ip(request))
    ua = (request.META.get('HTTP_USER_AGENT', '') or '')[:300]
    user = getattr(request, 'user', None)
    user_obj = user if user is not None and getattr(user, 'is_authenticated', False) else None

    try:
        obj = CookieConsent.objects.get(consent_id=cid)
        changed = (obj.statistics != statistics) or (obj.marketing != marketing)
    except CookieConsent.DoesNotExist:
        obj, changed = None, True
        is_new = True

    if obj is None:
        obj = CookieConsent.objects.create(
            consent_id=cid,
            session_key=session_key,
            user=user_obj,
            essential=True,
            statistics=statistics,
            marketing=marketing,
            policy_version=policy_version,
            ip_hash=ip_hash,
            user_agent=ua,
        )
    else:
        obj.session_key = session_key or obj.session_key
        if user_obj is not None and obj.user_id is None:
            obj.user = user_obj
        obj.statistics = statistics
        obj.marketing = marketing
        obj.policy_version = policy_version
        obj.ip_hash = ip_hash
        if ua:
            obj.user_agent = ua
        obj.save()

    # Log preuve append-only (nouveau ou choix modifié).
    if is_new or changed:
        CookieConsentLog.objects.create(
            consent=obj,
            action=action if action in ('accept_all', 'reject_all', 'save_prefs', 'sync') else 'save',
            statistics=statistics,
            marketing=marketing,
            policy_version=policy_version,
            ip_hash=ip_hash,
            user_agent=ua,
        )

    # Miroir session pour usage template immédiat.
    request.session['cookie_statistics'] = statistics
    request.session['cookie_marketing'] = marketing

    resp = JsonResponse({
        'status': 'ok',
        'essential': True,
        'statistics': statistics,
        'marketing': marketing,
        'has_consented': True,
        'consent_id': str(obj.consent_id),
        'policy_version': policy_version,
    })
    resp.set_cookie(
        cookie_name, str(obj.consent_id), max_age=cookie_age,
        httponly=False, samesite='Lax',
        secure=(not _settings.DEBUG),
        path='/',
    )
    return resp
