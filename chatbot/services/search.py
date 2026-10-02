import html as html_module
import re
import unicodedata
from django.apps import apps
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
from chatbot.models import ChatbotKnowledge

# Chaque entrée : (app_label, ModelName, [champs texte])
# L'ordre = priorité à score égal. Champs adaptés aux modèles BS GROUP.
TEXT_FIELDS = [
    ('services', 'Service', [
        'title', 'excerpt', 'category', 'timeline', 'team_size', 'warranty',
        'intro', 'approach_title', 'approach',
        'includes_title', 'includes_description',
        'benefits_title', 'benefits_description',
        'process_title', 'process_description',
    ]),
    ('services', 'ServiceFeature', ['title']),
    ('services', 'ServiceBenefit', ['title', 'description']),
    ('services', 'ServiceStep', ['number', 'title', 'description']),
    ('blog', 'Post', ['title', 'category', 'author_name', 'excerpt', 'content', 'tags']),
    ('projects', 'Project', [
        'title', 'category', 'location', 'area', 'duration',
        'excerpt', 'intro', 'description',
        'challenge_title', 'challenge', 'solution_title', 'solution',
        'scope_title', 'scope_description', 'result_title', 'result',
        'testimonial_title', 'testimonial_text', 'testimonial_name',
    ]),
    ('projects', 'ProjectPoint', ['text']),
    ('projects', 'ProjectStep', ['number', 'title', 'description']),
    ('main', 'FAQ', ['question', 'answer']),
    ('main', 'SiteStat', ['label', 'value', 'suffix']),
    ('main', 'SkillBar', ['label']),
    ('main', 'ProcessStep', ['title', 'description']),
    ('main', 'Feature', ['title', 'description']),
    ('main', 'LegalPage', ['title', 'subtitle', 'description', 'intro']),
    ('main', 'LegalArticle', ['number', 'title', 'content']),
    ('main', 'Partner', ['name']),
    ('team', 'TeamMember', ['name', 'role', 'department', 'bio', 'bio_2', 'quote']),
    ('team', 'TeamExperience', ['period', 'title', 'description']),
    ('team', 'TeamCertification', ['title']),
    ('team', 'Testimonial', ['client_name', 'client_role', 'title', 'text']),
    ('careers', 'CareerPage', ['hero_title', 'hero_subtitle', 'openings_title', 'openings_subtitle']),
    ('careers', 'Perk', ['title', 'description']),
    ('careers', 'JobOpening', [
        'title', 'department', 'location', 'job_type', 'experience',
        'salary', 'description', 'responsibilities', 'requirements',
    ]),
    # SiteSettings est indexé à part (singleton, pas de slug) : voir _site_settings_hits().
]

VALID_LANGS = {'fr', 'en', 'ar'}

# Plafond de lignes scannées par modèle (matching Python insensible aux accents).
_MAX_ROWS_PER_MODEL = 500

# Intentions détectées sur tokens normalisés (minuscules, sans accents).
_SERVICE_INTENT = frozenset("""
service services prestation prestations activite activites domaine domaines
offre offres solution solutions aide aider aidez proposer proposez faites
faire catalogue realisation realisations metier metiers
offer offers offering offerings activity activities solution solutions
provide provides help catalog business
خدمة خدمات نشاط انشطة عرض عروض مجال مجالات
""".split())

_CONTACT_INTENT = frozenset("""
contact contacter contactez contacte joindre appel appeler appelez
email mail courriel telephone tel adresse address localisation siege
bureau bureaux whatsapp numero coordonnees horaires ouverture
phone email address location contact call reach headquarters office
اتصل اتصلوا هاتف الهاتف بريد ايميل عنوان مقر موقع رقم الهاتف
""".split())

# Mots vides par langue (FR/EN/AR).
_STOPWORDS = frozenset("""
le la les de des du un une et est sont vos votre nos notre vous nous
il ils elle elles on ce ces cet cette dans pour avec sur par plus pas
au aux en du quel quelle quels quelles quoi qui que est-ce comment
combien pourquoi quand quel quels votre vos ton ta tes mon ma mes
the a an and is are your our you we it this that these those in for with
on by what how which who where when much many does do did has have can
""".split())


def _safe_lang(lang):
    return lang if lang in VALID_LANGS else 'fr'


def _normalize(text):
    """Minuscules + sans accents (+ arabe tel quel)."""
    text = (text or '').lower()
    text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in text if not unicodedata.combining(c))


def truncate_html(text, max_words=80):
    """Strip HTML, unescape entities, truncate to N words."""
    plain = strip_tags(text or '')
    plain = html_module.unescape(plain)
    return Truncator(plain).words(max_words, truncate='…')


def _model_field_names(model):
    return {f.name for f in model._meta.get_fields()}


def _search_fields(model, model_fields, lang):
    """Champs traduits d'abord (titre_fr...), puis champs de base — uniquement existants."""
    lang = _safe_lang(lang)
    existing = _model_field_names(model)
    result = []
    for f in model_fields:
        if f'{f}_{lang}' in existing:
            result.append(f'{f}_{lang}')
        if f in existing:
            result.append(f)
    return result


def _get_field_value(obj, base_field, lang):
    """Priorité à la langue demandée (la thread Django n'est pas forcément dans `lang`)."""
    lang_val = getattr(obj, f'{base_field}_{lang}', None)
    if lang_val:
        return str(lang_val)
    base_val = getattr(obj, base_field, None)
    if base_val:
        return str(base_val)
    return ''


def _tokenize(query):
    """Minuscules, sans accents, découpe mot (latin + arabe), retire stopwords + tokens < 3 lettres."""
    norm = _normalize(query)
    tokens = re.findall(r'[a-z0-9\u0600-\u06ff]+', norm)
    meaningful = [t for t in tokens if len(t) >= 3 and t not in _STOPWORDS]
    # Si tout est stopword ("c'est quoi ?"), garde les tokens longs quand même
    if not meaningful:
        meaningful = [t for t in tokens if len(t) >= 2]
    return meaningful


def _score_fields(obj, fields, tokens, lang):
    """
    Score insensible aux accents calculé en Python (pas de icontains SQL,
    qui rate 'negoce' vs 'Négoce'). Retourne (score_total, [(score, texte)]).
    Le premier champ (souvent le titre) compte double.
    """
    total = 0
    per_field = []
    for i, f in enumerate(fields):
        val = _get_field_value(obj, f, lang)
        s = _score(val, tokens)
        if i == 0:
            s *= 2
        total += s
        if (val or '').strip():
            per_field.append((s, val))
    return total, per_field


def _rich_excerpt(title, per_field, max_words=120):
    """
    Extrait substantiel : titre + meilleurs champs correspondants, avec
    toujours au moins les 2 premiers champs non vides (souvent l'accroche
    et l'intro) même sans match direct — sinon Gemini reçoit juste un
    titre ('BTP') et répond 'pas d'info'.
    """
    ranked = sorted(
        enumerate(per_field),
        key=lambda t: (t[1][0] <= 0, -t[1][0], t[0]),
    )
    chunks = [title] if (title or '').strip() else []
    seen = {title.strip().lower()} if chunks else set()
    for _, (s, val) in ranked:
        v = (val or '').strip()
        if not v or v.lower() in seen:
            continue
        chunks.append(v)
        seen.add(v.lower())
        if len(chunks) >= 4:
            break
    return truncate_html(' — '.join(chunks), max_words=max_words)


def _obj_title(obj, lang):
    title = (
        getattr(obj, f'title_{lang}', None)
        or getattr(obj, 'title', None)
        or getattr(obj, f'question_{lang}', None)
        or getattr(obj, 'question', None)
        or getattr(obj, f'name_{lang}', None)
        or getattr(obj, 'name', None)
        or getattr(obj, 'client_name', None)
        or str(obj)
    )
    return str(title)


def _obj_url(obj):
    """Build URL for a search hit, or None."""
    label = obj._meta.app_label
    model = obj._meta.model_name
    slug = getattr(obj, 'slug', None)
    if not slug:
        return None
    try:
        if label == 'services' and model == 'service':
            return reverse('services:service-detail', args=[slug])
        if label == 'blog' and model == 'post':
            return reverse('blog:blog-detail', args=[slug])
        if label == 'projects' and model == 'project':
            return reverse('projects:projet-detail', args=[slug])
        if label == 'team' and model == 'teammember':
            return reverse('team:team-detail', args=[slug])
        if label == 'careers' and model == 'jobopening':
            return reverse('careers:career-detail', args=[slug])
    except Exception:
        return None
    return None


def _score(text, tokens):
    """Chaque token distinct trouvé ajoute 10 pts (match insensible aux accents)."""
    if not text:
        return 0
    low = _normalize(str(text))
    return sum(10 for t in tokens if t in low)


def _site_settings_hits(tokens, lang):
    """Le singleton SiteSettings (téléphone, email, adresse, hero, about...)."""
    try:
        SiteSettings = apps.get_model('main', 'SiteSettings')
        ss = SiteSettings.objects.first()
    except LookupError:
        return []
    if not ss:
        return []
    contact_block = ' '.join(filter(None, [
        _get_field_value(ss, 'company_name', lang),
        _get_field_value(ss, 'footer_description', lang),
        getattr(ss, 'phone', '') or '',
        getattr(ss, 'email', '') or '',
        getattr(ss, 'careers_email', '') or '',
        _get_field_value(ss, 'address', lang),
        _get_field_value(ss, 'hero_badge', lang),
        _get_field_value(ss, 'hero_title', lang),
        _get_field_value(ss, 'hero_description', lang),
        _get_field_value(ss, 'about_title', lang),
        _get_field_value(ss, 'about_description', lang),
        _get_field_value(ss, 'about_description_2', lang),
        _get_field_value(ss, 'vision_title', lang),
        _get_field_value(ss, 'vision_description', lang),
        _get_field_value(ss, 'mission_title', lang),
        _get_field_value(ss, 'mission_description', lang),
        _get_field_value(ss, 'services_section_title', lang),
    ]))
    score = _score(contact_block, tokens)
    if score <= 0:
        return []
    return [{
        'title': _get_field_value(ss, 'company_name', lang) or 'BS GROUP',
        'excerpt': truncate_html(contact_block, max_words=100),
        'source_url': None,
        'score': score + 5,  # léger bonus : infos entreprise souvent demandées
    }]


def _contact_hit(lang):
    """
    Intention contact explicite : renvoie directement les coordonnées
    de la BD (téléphone, email, adresse), même si les mots 'email' ou
    'téléphone' ne figurent dans aucun texte du site.
    """
    try:
        SiteSettings = apps.get_model('main', 'SiteSettings')
        ss = SiteSettings.objects.first()
    except LookupError:
        return None
    if not ss:
        return None
    parts = []
    company = _get_field_value(ss, 'company_name', lang) or 'BS GROUP'
    for label, val in (
        ('Téléphone', (getattr(ss, 'phone', '') or '').strip()),
        ('Email', (getattr(ss, 'email', '') or '').strip()),
        ('Email carrières', (getattr(ss, 'careers_email', '') or '').strip()),
        ('Adresse', _get_field_value(ss, 'address', lang).strip()),
    ):
        if val:
            parts.append(f'{label} : {val}')
    if not parts:
        return None
    return {
        'title': f'{company} — Contact',
        'excerpt': truncate_html(' — '.join(parts), max_words=100),
        'source_url': None,
        'score': 60,  # prioritaire quand l'intention contact est explicite
    }


def _service_catalog_hits(lang, exclude_titles, count=6):
    """
    Repli catalogue : la question porte sur les services en général
    ('quels sont vos services ?') mais aucun mot ne matche les contenus.
    Retourne les premiers services avec un extrait substantiel.
    """
    try:
        Service = apps.get_model('services', 'Service')
    except LookupError:
        return []
    hits = []
    for obj in Service.objects.order_by('order', 'id')[:count]:
        title = _obj_title(obj, lang)
        if title in exclude_titles:
            continue
        excerpt = _rich_excerpt(title, [
            (1, _get_field_value(obj, 'excerpt', lang)),
            (1, _get_field_value(obj, 'intro', lang)),
            (0, _get_field_value(obj, 'category', lang)),
        ])
        hits.append({
            'title': title,
            'excerpt': excerpt,
            'source_url': _obj_url(obj),
            'score': 5,
        })
        exclude_titles.add(title)
    return hits


def search_hits(query, lang, limit=6):
    """
    Search site models + ChatbotKnowledge for relevant content.
    Returns list of dicts: {title, excerpt, source_url, score}.
    """
    tokens = _tokenize(query)
    if not tokens:
        return []

    lang = _safe_lang(lang)
    hits = []

    # Données dynamiques du site (singleton) — toujours évaluées
    hits.extend(_site_settings_hits(tokens, lang))

    # Search ChatbotKnowledge (active only, no modeltranslation)
    for kb in ChatbotKnowledge.objects.filter(is_active=True)[:100]:
        score = _score(kb.content, tokens) + _score(kb.name, tokens) * 2
        if score > 0:
            hits.append({
                'title': kb.name,
                'excerpt': truncate_html(kb.content, max_words=100),
                'source_url': None,
                'score': score,
            })

    # Search site content models — matching 100 % Python, insensible
    # aux accents (le préfiltre SQL icontains ratait 'negoce' vs 'Négoce').
    existing_titles = {h['title'] for h in hits}
    for app_label, model_name, fields in TEXT_FIELDS:
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            continue

        try:
            rows = list(Model.objects.all()[:_MAX_ROWS_PER_MODEL])
        except Exception:
            continue
        for obj in rows:
            title = _obj_title(obj, lang)
            if title in existing_titles:
                continue
            obj_score, per_field = _score_fields(obj, fields, tokens, lang)
            if obj_score > 0:
                hits.append({
                    'title': title,
                    'excerpt': _rich_excerpt(title, per_field),
                    'source_url': _obj_url(obj),
                    'score': obj_score,
                })
                existing_titles.add(title)

    # Replis d'intention (seulement si le matching direct est pauvre)
    if any(t in _CONTACT_INTENT for t in tokens):
        contact = _contact_hit(lang)
        if contact and contact['title'] not in existing_titles:
            hits.append(contact)
            existing_titles.add(contact['title'])
    if len(hits) < 2 and any(t in _SERVICE_INTENT for t in tokens):
        hits.extend(_service_catalog_hits(lang, existing_titles))

    # Sort by score descending, return top N
    hits.sort(key=lambda h: h['score'], reverse=True)
    return hits[:limit]
