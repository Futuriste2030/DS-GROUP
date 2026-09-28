import uuid

from django.conf import settings


class CookieConsentMiddleware:
    """
    Lit le consentement cookies SANS créer de session (pas de gonflement bots)
    — même logique que DIGI-AGENCY.

    Ordre de recherche :
      1. cookie `consent_id` (UUID stable, 13 mois) -> ligne DB.
      2. Legacy : session_key Django -> ligne DB (installations pré-UUID).
      3. Données session posées par l'API consentement (usage immédiat après POST).

    Injecte `request.cookie_consent` pour vues et templates :
        {'essential': True, 'statistics': bool, 'marketing': bool,
         'has_consented': bool, 'consent_id': str | None}
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cookie_consent = self._get_consent(request)
        return self.get_response(request)

    def _get_consent(self, request):
        empty = {
            'essential': True,
            'statistics': False,
            'marketing': False,
            'has_consented': False,
            'consent_id': None,
        }

        # 1. ID stable d'abord — aucune création de session ici.
        cookie_name = getattr(settings, 'CONSENT_COOKIE_NAME', 'consent_id')
        raw_id = request.COOKIES.get(cookie_name)
        if raw_id:
            try:
                cid = uuid.UUID(str(raw_id))
            except (ValueError, AttributeError):
                cid = None
            if cid:
                try:
                    from main.models import CookieConsent
                    obj = CookieConsent.objects.get(consent_id=cid)
                    return {
                        'essential': True,
                        'statistics': obj.statistics,
                        'marketing': obj.marketing,
                        'has_consented': True,
                        'consent_id': str(obj.consent_id),
                    }
                except Exception:
                    pass

        # 2. Recherche legacy par session_key — lecture seule, jamais de création.
        session_key = getattr(getattr(request, 'session', None), 'session_key', None)
        if session_key:
            try:
                from main.models import CookieConsent
                obj = CookieConsent.objects.filter(session_key=session_key).order_by('-updated_at').first()
                if obj:
                    return {
                        'essential': True,
                        'statistics': obj.statistics,
                        'marketing': obj.marketing,
                        'has_consented': True,
                        'consent_id': str(obj.consent_id),
                    }
            except Exception:
                pass

            # 3. Repli : données session écrites par l'API juste après POST.
            try:
                stats = request.session.get('cookie_statistics', None)
                mkt = request.session.get('cookie_marketing', None)
            except Exception:
                stats = mkt = None
            if stats is not None and mkt is not None:
                return {
                    'essential': True,
                    'statistics': bool(stats),
                    'marketing': bool(mkt),
                    'has_consented': True,
                    'consent_id': str(raw_id) if raw_id else None,
                }

        # Pas encore de consentement
        return empty
