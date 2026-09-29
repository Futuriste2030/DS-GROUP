"""Tags SEO — même logique que DIGI-AGENCY (hreflang FR/EN/AR)."""
from django import template
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, activate
from django.conf import settings

register = template.Library()


@register.filter
def splitlines(value):
    """Split a multi-line admin text into a list (one option per line)."""
    if not value:
        return []
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def _swap_lang_prefix(path, lang_code):
    """Swap or add the language prefix, respecting prefix_default_language=False."""
    codes = [code for code, _ in settings.LANGUAGES]
    rest = path
    for code in codes:
        if path == f'/{code}':
            rest = '/'
            break
        if path.startswith(f'/{code}/'):
            rest = path[len(code) + 1:]
            break
    default_lang = getattr(settings, 'MODELTRANSLATION_DEFAULT_LANGUAGE', None) or settings.LANGUAGE_CODE
    if lang_code == default_lang:
        return rest or '/'
    return f'/{lang_code}{rest}' if rest.startswith('/') else f'/{lang_code}/{rest}'


@register.simple_tag(takes_context=True)
def hreflang_links(context):
    """Render <link rel="alternate" hreflang="..."> tags + x-default.

    Usage: {% hreflang_links %}
    """
    request = context.get('request')
    if request is None:
        return ''
    current_lang = get_language()
    match = getattr(request, 'resolver_match', None)
    view_name = getattr(match, 'view_name', None)
    kwargs = dict(getattr(match, 'kwargs', {}) or {})
    default_lang = getattr(settings, 'MODELTRANSLATION_DEFAULT_LANGUAGE', None) or settings.LANGUAGE_CODE

    tags = []
    default_href = ''
    for lang_code, _ in settings.LANGUAGES:
        url = None
        if view_name:
            try:
                activate(lang_code)
                url = reverse(view_name, kwargs=kwargs)
            except Exception:
                url = None
            finally:
                activate(current_lang)
        if not url:
            url = _swap_lang_prefix(request.path, lang_code)
        href = request.build_absolute_uri(url)
        if lang_code == default_lang:
            default_href = href
        tags.append(
            f'<link rel="alternate" hreflang="{escape(lang_code)}" href="{escape(href)}">'
        )
    if default_href:
        tags.append(
            f'<link rel="alternate" hreflang="x-default" href="{escape(default_href)}">'
        )
    return mark_safe('\n    '.join(tags))
