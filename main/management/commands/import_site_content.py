"""
Import des contenus transverses BS-GROUP depuis des fichiers TXT (FR/EN/AR).
Même logique que import_services : parsing TXT -> remplissage BD via modeltranslation.

Fichiers (racine projet) :
    faqs.txt         -> main.FAQ (question/answer, catégorie + ordre)
    features.txt     -> main.Feature (icon, title/description)
    process_step.txt -> main.ProcessStep (number, icon, title/description)
    site_stats.txt   -> main.SiteStat (value, suffix, label)
    skill_bar.txt    -> main.SkillBar (label, percentage)
    site_setting.txt -> main.SiteSettings (singleton ; remplit les champs vides
                        ou encore au défaut du modèle, conserve les valeurs
                        personnalisées par le client, comme l'indique la légende)
    career_page.txt  -> careers.CareerPage (singleton ; MAJ partielle comme settings)
    hiring_steps.txt -> careers.HiringStep (title/description, ordre)
    perks.txt        -> careers.Perk (icon, title/description)
    legals.txt       -> main.LegalPage + LegalArticle (4 pages, MAJ par page_type)
    posts.txt        -> blog.Post (MAJ par slug, contenu HTML conservé tel quel)
    team.txt         -> team.TeamMember (+experiences/certifications, MAJ par slug)
    timeline_event.txt -> main.TimelineEvent (year, title/description)

Usage:
    python manage.py import_site_content
    python manage.py import_site_content --only faqs features
    python manage.py import_site_content --dry-run
"""
import re
import unicodedata
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from blog.models import Post
from careers.models import CareerPage, HiringStep, Perk
from main.models import (
    FAQ, Feature, LegalArticle, LegalPage, ProcessStep, SiteSettings,
    SiteStat, SkillBar, TimelineEvent,
)
from team.models import TeamCertification, TeamExperience, TeamMember

LANGS = ('fr', 'en', 'ar')
LANG_RE = r'\[(FR|EN|AR)\]'

FILE_DEFAULTS = {
    'faqs': 'faqs.txt',
    'features': 'features.txt',
    'process': 'process_step.txt',
    'stats': 'site_stats.txt',
    'skills': 'skill_bar.txt',
    'settings': 'site_setting.txt',
    'career_page': 'career_page.txt',
    'hiring': 'hiring_steps.txt',
    'perks': 'perks.txt',
    'legals': 'legals.txt',
    'posts': 'posts.txt',
    'team': 'team.txt',
    'timeline': 'timeline_event.txt',
}

FAQ_CATEGORIES = {
    'General': 'general',
    'Services & Process': 'process',
    'Payments & Budget': 'payments',
    'Warranty & Support': 'warranty',
}


def _split_key_value(line):
    if ' : ' in line:
        k, v = line.split(' : ', 1)
        return k.strip(), v.strip()
    if ':' in line:
        k, v = line.split(':', 1)
        return k.strip(), v.strip()
    return line.strip(), ''


def _is_placeholder(value):
    v = (value or '').strip()
    if v == '' or v.lower() == '(vide)':
        return True
    vl = v.lower()
    return v.startswith('(') and ('à ' in vl or 'ex.' in vl or 'conserver' in vl or 'vide' in vl)


def _strip_trailing_note(value):
    """Retire une annotation finale '(...)' : 'BS GROUP (prérempli — conserver)' -> 'BS GROUP'."""
    v = (value or '').strip()
    return re.sub(r'\s*\([^()]*\)\s*$', '', v).strip()


def _read_lines(path):
    p = Path(path)
    if not p.is_absolute():
        p = Path(settings.BASE_DIR) / path
    if not p.exists():
        raise FileNotFoundError(f'Fichier introuvable : {p}')
    return p.read_text(encoding='utf-8').splitlines(), p


# ---------------------------------------------------------------- FAQ ---
def parse_faqs(path):
    lines, _ = _read_lines(path)
    faqs, cur, section = [], None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'FAQ\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and (cur['fr'].get('question') or cur['order'] is not None):
                faqs.append(cur)
            cur = {'category': 'general', 'order': None, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            kl = key.lower()
            if kl == 'category':
                cur['category'] = FAQ_CATEGORIES.get(value.strip(), 'general')
            elif kl == 'order':
                try:
                    cur['order'] = int(value.strip())
                except ValueError:
                    cur['order'] = None
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*(Question|Answer)\s*:\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            cur[m.group(1).lower()][m.group(2).lower()] = m.group(3).strip()
    if cur and (cur['fr'].get('question') or cur['order'] is not None):
        faqs.append(cur)
    return faqs


# ------------------------------------------------------------ FEATURES ---
def parse_features(path):
    lines, _ = _read_lines(path)
    items, cur, section = [], None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'FEATURE\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and cur['fr'].get('title'):
                items.append(cur)
            cur = {'icon': '', 'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            kl = key.lower()
            if kl == 'icon':
                cur['icon'] = value
            elif kl == 'order':
                try:
                    cur['order'] = int(value)
                except ValueError:
                    pass
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*(Title|Description)\s*:\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            cur[m.group(1).lower()][m.group(2).lower()] = m.group(3).strip()
    if cur and cur['fr'].get('title'):
        items.append(cur)
    return items


# -------------------------------------------------------- PROCESS STEPS ---
def parse_process_steps(path):
    lines, _ = _read_lines(path)
    items, cur = [], None
    section = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'STEP\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and cur['fr'].get('title'):
                items.append(cur)
            cur = {'number': 0, 'icon': '', 'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            kl = key.lower()
            if kl == 'number':
                try:
                    cur['number'] = int(re.sub(r'\D', '', value) or 0)
                except ValueError:
                    pass
            elif kl == 'icon':
                cur['icon'] = value
            elif kl == 'order':
                try:
                    cur['order'] = int(value)
                except ValueError:
                    pass
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*(Title|Description)\s*:\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            cur[m.group(1).lower()][m.group(2).lower()] = m.group(3).strip()
    if cur and cur['fr'].get('title'):
        items.append(cur)
    return items


# ----------------------------------------------------------- SITE STATS ---
def parse_site_stats(path):
    lines, _ = _read_lines(path)
    items, cur = [], None
    section = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'STAT\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and (cur['fr'].get('label') or cur['value']):
                items.append(cur)
            cur = {'value': '', 'suffix': '', 'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            kl = key.lower()
            if kl == 'value':
                cur['value'] = value
            elif kl == 'suffix':
                cur['suffix'] = '' if _is_placeholder(value) else value
            elif kl == 'order':
                try:
                    cur['order'] = int(value)
                except ValueError:
                    pass
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*Label\s*:\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            cur[m.group(1).lower()]['label'] = m.group(2).strip()
    if cur and (cur['fr'].get('label') or cur['value']):
        items.append(cur)
    return items


# ----------------------------------------------------------- SKILL BARS ---
def parse_skill_bars(path):
    lines, _ = _read_lines(path)
    items, cur = [], None
    section = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'SKILL\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and cur['fr'].get('label'):
                items.append(cur)
            cur = {'percentage': 0, 'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            kl = key.lower()
            if kl == 'percentage':
                try:
                    cur['percentage'] = int(re.sub(r'\D', '', value) or 0)
                except ValueError:
                    pass
            elif kl == 'order':
                try:
                    cur['order'] = int(value)
                except ValueError:
                    pass
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*Label\s*:\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            cur[m.group(1).lower()]['label'] = m.group(2).strip()
    if cur and cur['fr'].get('label'):
        items.append(cur)
    return items


# ------------------------------------------------------- SITE SETTINGS ---
# Libellé TXT (sans note entre parenthèses) -> champ modèle.
SETTINGS_FIELDS = {
    'Company name': 'company_name',
    'Company short name': 'company_short_name',
    'Site url': 'site_url',
    'Meta author': 'meta_author',
    'Meta description': 'meta_description',
    'Meta keywords': 'meta_keywords',
    'Phone': 'phone',
    'Email': 'email',
    'Careers email': 'careers_email',
    'Map query': 'map_query',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Address': 'address',
    'Opening hours weekdays': 'opening_hours_weekdays',
    'Opening hours weekend': 'opening_hours_weekend',
    'About title': 'about_title',
    'About description': 'about_description',
    'About description 2': 'about_description_2',
    'About section title': 'about_section_title',
    'About section subtitle': 'about_section_subtitle',
    'About badge value': 'about_badge_value',
    'About badge suffix': 'about_badge_suffix',
    'Vision title': 'vision_title',
    'Vision description': 'vision_description',
    'Mission title': 'mission_title',
    'Mission description': 'mission_description',
    'Process title': 'process_title',
    'Process description': 'process_description',
    'Why subtitle': 'why_subtitle',
    'Why title': 'why_title',
    'Hero badge': 'hero_badge',
    'Hero title': 'hero_title',
    'Hero description': 'hero_description',
    'Services section title': 'services_section_title',
    'Facebook url': 'facebook_url',
    'Twitter url': 'twitter_url',
    'Instagram url': 'instagram_url',
    'Youtube url': 'youtube_url',
    'Pinterest url': 'pinterest_url',
    'About video url': 'about_video_url',
    'Hero video url': 'hero_video_url',
}
# Champs image / sans import TXT (téléversés via admin).
SETTINGS_SKIP = {
    'Logo', 'About image 1', 'About image 2', 'Why image 1', 'Why image 2',
    'Hero image', 'Hero image 1', 'Hero image 2', 'Hero image 3',
    'About video cover', 'Hero video cover', 'Contact image',
}


def parse_site_settings(path):
    lines, _ = _read_lines(path)
    data = {'non_trad': {}, 'fr': {}, 'en': {}, 'ar': {}, 'notes': []}
    pending_trad = None       # champ traduit en cours ([FR]/[EN]/[AR] à venir)
    pending_options = None    # 'quote_budget_options' | 'quote_timeline_options'
    fr_options = []

    def flush_options():
        nonlocal pending_options, fr_options
        pending_options, fr_options = None, []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Sections '1. COMPANY' ... '9. SECTIONS'
        if re.match(r'^\d+\.\s+', line):
            pending_trad, pending_options, fr_options = None, None, []
            continue
        low = line.lower()
        if low.startswith('champs non traduits') or low.startswith('champs traduits'):
            continue
        # Lignes de notes / variantes / conseils : ignorées.
        if line.startswith(('Note', 'Option ', 'Variante ', 'Si le client')) or '⚠' in line:
            continue

        # Traductions des listes d'options devis : 'Traductions EN ... : a / b / c'
        m_opt = re.match(r'^Traductions\s+(EN|AR)\b\s*(?:\([^)]*\))?\s*:\s*(.+)$', line, re.IGNORECASE)
        if m_opt and pending_options:
            lang = m_opt.group(1).lower()
            items = [s.strip() for s in m_opt.group(2).split(' / ') if s.strip()]
            data[lang][pending_options] = '\n'.join(items)
            if lang == 'ar':
                flush_options()
            continue

        # Valeurs traduites '[FR] ...'
        m_lang = re.match(r'^\[(FR|EN|AR)\]\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m_lang:
            lang, text = m_lang.group(1).lower(), m_lang.group(2).strip()
            if pending_trad and text and not _is_placeholder(text):
                data[lang][pending_trad] = text
            elif not pending_trad and lang == 'fr' and text:
                # Bloc LEGAL sans libellé : extrait RCCM + NINA (champs réels).
                m_rccm = re.search(r'RCCM\s*:\s*([A-Z0-9.]+)', text)
                if m_rccm:
                    data['non_trad']['rccm'] = m_rccm.group(1)
                m_nina = re.search(r'NINA\s*:\s*([A-Z0-9]+)', text)
                if m_nina:
                    data['non_trad']['nif'] = m_nina.group(1)
            continue

        # Listes d'options FR (lignes simples après le libellé 'Quote ... options')
        if pending_options and not line.startswith('[') and ' : ' not in line and ':' not in line.split(' ', 1)[0]:
            fr_options.append(line)
            data['fr'][pending_options] = '\n'.join(fr_options)
            continue

        # Libellés de champs : 'Company name : valeur' ou 'Footer description' seul
        if ' : ' in line or ':' in line:
            key, value = _split_key_value(line)
        else:
            key, value = line, ''
        base_label = re.sub(r'\s*\([^()]*\)\s*$', '', key).strip()

        if base_label in ('Quote budget options', 'Quote timeline options'):
            pending_options = 'quote_budget_options' if 'budget' in base_label.lower() else 'quote_timeline_options'
            fr_options = []
            pending_trad = None
            continue
        if base_label in SETTINGS_SKIP:
            pending_trad = None
            flush_options()
            continue
        field = SETTINGS_FIELDS.get(base_label)
        if not field:
            pending_trad = None
            continue
        if value:
            cleaned = _strip_trailing_note(value)
            if cleaned and not _is_placeholder(cleaned):
                data['non_trad'][field] = cleaned
            pending_trad = None
            flush_options()
        else:
            # Libellé seul -> les lignes [FR]/[EN]/[AR] suivantes alimentent ce champ
            pending_trad = field
    return data


def _is_note(value):
    """Valeur entièrement entre parenthèses : indication de saisie, pas un contenu."""
    v = (value or '').strip()
    return len(v) >= 2 and v.startswith('(') and v.endswith(')')


def _to_int(value, default=0):
    try:
        return int(re.sub(r'\D', '', str(value or '')) or default)
    except (TypeError, ValueError):
        return default


def _to_bool(value):
    v = (value or '').strip().lower()
    if v in ('coché', 'coche', 'checked', 'oui', 'yes', 'true', '1', 'x'):
        return True
    return False


def _norm_label(value):
    """Minuscules sans accents, espaces normalisés (pour mapper les libellés FR)."""
    s = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s).strip().lower()


def _parse_date(value):
    v = (value or '').strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y'):
        try:
            from datetime import datetime
            return datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


def _clean_text(value, keep_lines=False):
    """Nettoie une valeur accumulée : notes ignorées, espaces normalisés."""
    v = (value or '').strip()
    if not v or _is_note(v) or _is_placeholder(v):
        return ''
    if keep_lines:
        return '\n'.join([ln.strip() for ln in v.splitlines() if ln.strip()])
    return ' '.join(v.split())


# ------------------------------------------- BLOC GÉNÉRIQUE TITRÉ (hiring/perks/timeline) ---
def parse_titled_blocks(path, header_re):
    """Blocs 'STEP/PERK/EVENT n / m' : non-traduits 'Clé : valeur' + traduits '[FR] Champ : valeur'."""
    lines, _ = _read_lines(path)
    items, cur, section = [], None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(header_re, line, re.IGNORECASE):
            if cur and cur['fr']:
                items.append(cur)
            cur = {'nontrad': {}, 'fr': {}, 'en': {}, 'ar': {}}
            section = None
            continue
        if cur is None:
            continue
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = 'TRADUIT'
            continue
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
            cur['nontrad'][key.strip().lower()] = value.strip()
            continue
        m = re.match(r'\[(FR|EN|AR)\]\s*([A-Za-z ]+?)\s*:\s*(.*)$', line)
        if m:
            text = _clean_text(m.group(3))
            if text:
                cur[m.group(1).lower()][m.group(2).strip().lower()] = text
    if cur and cur['fr']:
        items.append(cur)
    return items


# -------------------------------------------------------------- CAREER PAGE ---
# Libellé TXT (sans variante '— ...' ni note '(...)') -> champ modèle.
CAREER_FIELDS = {
    'Hero title': 'hero_title',
    'Hero subtitle': 'hero_subtitle',
    'Hero description': 'hero_description',
    'Openings title': 'openings_title',
    'Openings subtitle': 'openings_subtitle',
}


def _career_label(line):
    # D'abord la note finale '(...)' (elle peut contenir '—'), puis la variante ' — ...'.
    base = re.sub(r'\s*\([^()]*\)\s*$', '', line.strip()).strip()
    return re.split(r'\s+[—–-]\s+', base, maxsplit=1)[0].strip()


def parse_career_page(path):
    lines, _ = _read_lines(path)
    data = {'non_trad': {}, 'fr': {}, 'en': {}, 'ar': {}}
    pending = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'^\d+\.\s+', line):
            pending = None
            continue
        low = line.lower()
        if low.startswith(('champs non traduits', 'champs traduits')):
            pending = None
            continue
        m = re.match(r'^\[(FR|EN|AR)\]\s*(.*)$', line, re.IGNORECASE | re.DOTALL)
        if m:
            lang, text = m.group(1).lower(), _clean_text(m.group(2))
            # Première variante rencontrée gagne (VERSION RECOMMANDÉE avant VARIANTE B).
            # pending conservé : FR/EN/AR partagent le même libellé.
            if pending and text and pending not in data[lang]:
                data[lang][pending] = text
            continue
        if ':' in line or ' : ' in line:
            pending = None
            continue
        field = CAREER_FIELDS.get(_career_label(line))
        pending = field
    return data


# ------------------------------------------------------------------ LEGALS ---
# Libellé FR du select -> clé page_type du modèle.
LEGAL_PAGE_TYPES = {
    'mentions legales': 'legal',
    'politique de confidentialite': 'privacy',
    'cgu': 'cgu',
    'politique cookies': 'cookies',
}

LEGAL_PAGE_FIELDS = ('title', 'subtitle', 'description', 'intro')


def parse_legals(path):
    lines, _ = _read_lines(path)
    pages, page, article, pending = [], None, None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'PAGE\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if page and page['page_type']:
                pages.append(page)
            page = {'page_type': '', 'last_updated': None, 'version': '1.0',
                    'fr': {}, 'en': {}, 'ar': {}, 'articles': []}
            article, pending = None, None
            continue
        if page is None:
            continue
        low = line.lower()
        if low in ('champs non traduits', 'champs traduits', 'legal articles'):
            pending = None
            continue
        key, value = _split_key_value(line)
        kl = _norm_label(key)
        if kl == 'page type':
            page['page_type'] = LEGAL_PAGE_TYPES.get(_norm_label(_strip_trailing_note(value)), '')
            pending = None
            continue
        if kl == 'last updated':
            page['last_updated'] = _parse_date(value)
            pending = None
            continue
        if kl == 'version number':
            page['version'] = (value.strip() or '1.0')
            pending = None
            continue
        m_art = re.match(
            r'ARTICLE\s+\d+\s*[—–-]\s*(.+?)\s*\|\s*Number\s*:\s*(.+?)\s*\|\s*Order\s*:\s*(.+)$',
            line, re.IGNORECASE)
        if m_art:
            article = {'number': m_art.group(2).strip(),
                       'order': _to_int(m_art.group(3)),
                       'fr': {}, 'en': {}, 'ar': {}}
            page['articles'].append(article)
            pending = None
            continue
        m = re.match(r'^\[(FR|EN|AR)\]\s*(?:(Title|Subtitle|Description|Intro|Content)\s*:\s*)?(.*)$',
                     line, re.IGNORECASE | re.DOTALL)
        if m:
            lang, field, text = m.group(1).lower(), (m.group(2) or '').lower(), _clean_text(m.group(3))
            if not text:
                continue
            if field:
                if article is not None and field in ('title', 'content'):
                    article[lang][field] = text
                elif article is None and field in LEGAL_PAGE_FIELDS:
                    page[lang][field] = text
            elif pending and article is None:
                page[lang][pending] = text
            continue
        if article is None and _norm_label(line) in LEGAL_PAGE_FIELDS:
            pending = _norm_label(line)
        else:
            pending = None
    if page and page['page_type']:
        pages.append(page)
    return pages


# -------------------------------------------------------------------- POSTS ---
POST_LABELS = ('slug', 'image', 'order', 'title', 'category', 'author name',
               'author avatar', 'author bio', 'excerpt', 'content',
               'reading time', 'tags')
POST_FIELD_ATTR = {
    'slug': None, 'image': None, 'order': None,
    'title': 'title', 'category': 'category', 'author name': 'author_name',
    'author avatar': None, 'author bio': 'author_bio', 'excerpt': 'excerpt',
    'content': 'content', 'reading time': 'reading_time', 'tags': 'tags',
}
POST_LABEL_RE = re.compile(
    r'^(Slug|Image|Order|Title|Category|Author name|Author avatar|Author bio|'
    r'Excerpt|Content|Reading time|Tags)\s*:(.*)$', re.IGNORECASE)


def _acc_block(cur, lang, fname, val, first):
    """Accumule une valeur multi-lignes (Slug/Image/Order : 1re ligne non vide)."""
    if lang == 'nontrad':
        if fname == 'slug' and not cur['slug'] and val and not _is_note(val):
            cur['slug'] = val
        elif fname == 'order' and val:
            cur['order'] = _to_int(val, cur['order'])
        elif fname == 'image' and not cur.get('image') and val and not _is_note(val):
            cur['image'] = val
        return
    if first:
        cur[lang][fname] = val
    else:
        cur[lang][fname] = (cur[lang].get(fname, '') + '\n' + val).strip()


def parse_posts(path):
    lines, _ = _read_lines(path)
    posts, cur, lang, field = [], None, None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'POST\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and (cur['slug'] or cur['fr'].get('title')):
                posts.append(cur)
            cur = {'slug': '', 'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            lang, field = None, None
            continue
        if cur is None:
            continue
        if line.startswith('==='):
            up = line.strip('=').strip().lower()
            if 'non traduits' in up:
                lang = 'nontrad'
            elif 'onglet fr' in up:
                lang = 'fr'
            elif 'onglet en' in up:
                lang = 'en'
            elif 'onglet ar' in up:
                lang = 'ar'
            field = None
            continue
        m = POST_LABEL_RE.match(line)
        if m and lang:
            field = m.group(1).lower()
            _acc_block(cur, lang, field, m.group(2).strip(), first=True)
            continue
        if field and lang:
            _acc_block(cur, lang, field, line, first=False)
    if cur and (cur['slug'] or cur['fr'].get('title')):
        posts.append(cur)
    for p in posts:
        for lg in LANGS:
            for fname, val in list(p[lg].items()):
                if fname in ('content',):
                    p[lg][fname] = (val or '').strip()
                elif fname == 'skills':
                    p[lg][fname] = _clean_text(val, keep_lines=True)
                else:
                    p[lg][fname] = _clean_text(val)
    return posts


# --------------------------------------------------------------------- TEAM ---
MEMBER_NUMERIC = {'experience years': 'experience_years', 'projects count': 'projects_count',
                  'people led': 'people_led', 'awards count': 'awards_count'}
MEMBER_CONTACT = ('email', 'phone', 'facebook', 'twitter', 'instagram', 'linkedin')
MEMBER_TRAD_SIMPLE = ('name', 'role', 'department', 'bio', 'bio 2', 'quote', 'office')
TEAM_LABEL_RE = re.compile(
    r'^(Slug|Experience years|Projects count|People led|Awards count|Image|'
    r'Email|Phone|Facebook|Twitter|Instagram|Linkedin|Order|Name|Role|'
    r'Department|Bio|Bio 2|Quote|Skills|Office|Period|Title|Description|'
    r'Current|Certification)\s*:(.*)$', re.IGNORECASE)


def parse_team(path):
    lines, _ = _read_lines(path)
    members, cur, lang = [], None, None
    field, mode, sub = None, 'fields', None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if re.match(r'MEMBER\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if cur and (cur['slug'] or cur['fr'].get('name')):
                members.append(cur)
            cur = {'slug': '', 'order': 0, 'numeric': {}, 'contact': {},
                   'fr': {}, 'en': {}, 'ar': {}}
            lang, field, mode, sub = None, None, 'fields', None
            continue
        if cur is None:
            continue
        if line.startswith('==='):
            up = line.strip('=').strip().lower()
            if 'non traduits' in up:
                lang = 'nontrad'
            elif 'onglet fr' in up:
                lang = 'fr'
            elif 'onglet en' in up:
                lang = 'en'
            elif 'onglet ar' in up:
                lang = 'ar'
            field, mode, sub = None, 'fields', None
            continue
        if re.match(r'^Team experiences\s*:?\s*$', line, re.IGNORECASE):
            mode, field, sub = 'exps', None, None
            continue
        if re.match(r'^Team certifications\s*:?\s*$', line, re.IGNORECASE):
            mode, field, sub = 'certs', None, None
            continue
        if re.match(r'^Experience\s+\d+\s*$', line, re.IGNORECASE) and lang and lang != 'nontrad':
            sub = {'periods': {}, 'current': False, 'order': 0,
                   'fr': {}, 'en': {}, 'ar': {}}
            cur[lang].setdefault('experiences', []).append(sub)
            field = None
            continue
        if re.match(r'^Certification\s+\d+\s*$', line, re.IGNORECASE) and lang and lang != 'nontrad':
            sub = {'order': 0, 'fr': {}, 'en': {}, 'ar': {}}
            cur[lang].setdefault('certs', []).append(sub)
            field = None
            continue
        m = TEAM_LABEL_RE.match(line)
        if m and lang:
            field = m.group(1).lower()
            _acc_member(cur, lang, mode, sub, field, m.group(2).strip(), first=True)
            continue
        if field and lang:
            _acc_member(cur, lang, mode, sub, field, line, first=False)
    if cur and (cur['slug'] or cur['fr'].get('name')):
        members.append(cur)
    for mb in members:
        for lg in LANGS:
            for fname, val in list(mb[lg].items()):
                if fname == 'experiences':
                    for e in val:
                        for ll in LANGS:
                            for k in ('title', 'description'):
                                if k in e.get(ll, {}):
                                    e[ll][k] = _clean_text(e[ll][k])
                    continue
                if fname == 'certs':
                    for ct in val:
                        for ll in LANGS:
                            if 'title' in ct.get(ll, {}):
                                ct[ll]['title'] = _clean_text(ct[ll]['title'])
                    continue
                mb[lg][fname] = _clean_text(val, keep_lines=(fname == 'skills'))
    return members


def _acc_member(cur, lang, mode, sub, fname, val, first):
    if lang == 'nontrad':
        if fname == 'slug' and not cur['slug'] and val and not _is_note(val):
            cur['slug'] = val
        elif fname == 'order' and val:
            cur['order'] = _to_int(val, cur['order'])
        elif fname in MEMBER_NUMERIC and val and not _is_note(val):
            cur['numeric'][MEMBER_NUMERIC[fname]] = _to_int(val)
        elif fname in MEMBER_CONTACT or fname == 'image':
            if val and not _is_note(val) and not _is_placeholder(val):
                if fname == 'email' and '@' not in val:
                    return
                cur['contact'][fname] = val
        return
    if mode == 'exps' and sub is not None and fname in ('period', 'title', 'description', 'current', 'order'):
        if fname == 'period':
            if val and not _is_note(val):
                sub['periods'][lang] = val if first else (sub['periods'].get(lang, '') + ' ' + val).strip()
        elif fname == 'current':
            sub['current'] = sub['current'] or _to_bool(val)
        elif fname == 'order':
            sub['order'] = _to_int(val, sub['order'])
        else:
            key = fname
            sub[lang][key] = val if first else ((sub[lang].get(key, '') + '\n' + val).strip())
        return
    if mode == 'certs' and sub is not None and fname in ('title', 'order'):
        if fname == 'order':
            sub['order'] = _to_int(val, sub['order'])
        elif val and not _is_note(val):
            sub[lang]['title'] = val if first else ((sub[lang].get('title', '') + ' ' + val).strip())
        return
    if fname in MEMBER_TRAD_SIMPLE or fname == 'skills':
        cur[lang][fname] = val if first else ((cur[lang].get(fname, '') + '\n' + val).strip())


class Command(BaseCommand):
    help = ('Importe les contenus depuis les TXT (faqs, features, process, stats, skills, settings, '
            'career_page, hiring, perks, legals, posts, team, timeline).')

    def add_arguments(self, parser):
        parser.add_argument('--only', nargs='*', default=list(FILE_DEFAULTS),
                            help=f"Blocs à importer parmi : {', '.join(FILE_DEFAULTS)} (défaut : tous).")
        parser.add_argument('--dry-run', action='store_true', help='Parse seulement, sans écrire en BD.')

    def handle(self, *args, **options):
        only = [o for o in options['only'] if o in FILE_DEFAULTS]
        if not only:
            self.stderr.write(self.style.ERROR(f"--only invalide. Choix : {', '.join(FILE_DEFAULTS)}"))
            return
        dry = options['dry_run']

        plan = {}
        if 'faqs' in only:
            plan['faqs'] = parse_faqs(FILE_DEFAULTS['faqs'])
        if 'features' in only:
            plan['features'] = parse_features(FILE_DEFAULTS['features'])
        if 'process' in only:
            plan['process'] = parse_process_steps(FILE_DEFAULTS['process'])
        if 'stats' in only:
            plan['stats'] = parse_site_stats(FILE_DEFAULTS['stats'])
        if 'skills' in only:
            plan['skills'] = parse_skill_bars(FILE_DEFAULTS['skills'])
        if 'settings' in only:
            plan['settings'] = parse_site_settings(FILE_DEFAULTS['settings'])
        if 'career_page' in only:
            plan['career_page'] = parse_career_page(FILE_DEFAULTS['career_page'])
        if 'hiring' in only:
            plan['hiring'] = parse_titled_blocks(FILE_DEFAULTS['hiring'], r'STEP\s+\d+')
        if 'perks' in only:
            plan['perks'] = parse_titled_blocks(FILE_DEFAULTS['perks'], r'PERK\s+\d+')
        if 'legals' in only:
            plan['legals'] = parse_legals(FILE_DEFAULTS['legals'])
        if 'posts' in only:
            plan['posts'] = parse_posts(FILE_DEFAULTS['posts'])
        if 'team' in only:
            plan['team'] = parse_team(FILE_DEFAULTS['team'])
        if 'timeline' in only:
            plan['timeline'] = parse_titled_blocks(FILE_DEFAULTS['timeline'], r'EVENT\s+\d+')

        for name, items in plan.items():
            if name in ('settings', 'career_page'):
                n_trad = {k: len(v) for k, v in items.items() if k in ('fr', 'en', 'ar')}
                self.stdout.write(f'  - {name} : non_trad={len(items["non_trad"])} trad={n_trad}')
            elif name == 'legals':
                n_art = sum(len(p['articles']) for p in items)
                self.stdout.write(f'  - legals : {len(items)} page(s), {n_art} article(s)')
            else:
                self.stdout.write(f'  - {name} : {len(items)} entrée(s)')

        # Validation icônes (features + process steps + perks) contre le set Lucide local
        icons_dir = Path(settings.BASE_DIR) / 'static' / 'icons' / 'lucide'
        if icons_dir.is_dir() and ('features' in plan or 'process' in plan or 'perks' in plan):
            available = {f.stem for f in icons_dir.glob('*.svg')}
            used = set()
            for f in plan.get('features', []):
                if f.get('icon'):
                    used.add(f['icon'])
            for st in plan.get('process', []):
                if st.get('icon'):
                    used.add(st['icon'])
            for pk in plan.get('perks', []):
                if pk['nontrad'].get('icon'):
                    used.add(pk['nontrad']['icon'])
            missing = sorted(used - available)
            if missing:
                self.stdout.write(self.style.WARNING(
                    f'Icônes absentes de static/icons/lucide (invisibles) : {", ".join(missing)}'))
            else:
                self.stdout.write('Icônes : toutes présentes dans static/icons/lucide.')

        if dry:
            self.stdout.write(self.style.WARNING('Dry-run : rien écrit en BD.'))
            return

        with transaction.atomic():
            if 'faqs' in plan:
                FAQ.objects.all().delete()
                for f in plan['faqs']:
                    FAQ.objects.create(
                        category=f['category'], order=f['order'] or 0,
                        question_fr=f['fr'].get('question', ''), answer_fr=f['fr'].get('answer', ''),
                        question_en=f['en'].get('question', ''), answer_en=f['en'].get('answer', ''),
                        question_ar=f['ar'].get('question', ''), answer_ar=f['ar'].get('answer', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"FAQ : {len(plan['faqs'])} importée(s)."))

            if 'features' in plan:
                Feature.objects.all().delete()
                for f in plan['features']:
                    Feature.objects.create(
                        icon=f.get('icon', ''), order=f.get('order', 0),
                        title_fr=f['fr'].get('title', ''), description_fr=f['fr'].get('description', ''),
                        title_en=f['en'].get('title', ''), description_en=f['en'].get('description', ''),
                        title_ar=f['ar'].get('title', ''), description_ar=f['ar'].get('description', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"Features : {len(plan['features'])} importée(s)."))

            if 'process' in plan:
                ProcessStep.objects.all().delete()
                for st in plan['process']:
                    ProcessStep.objects.create(
                        number=st.get('number', 0), icon=st.get('icon', ''), order=st.get('order', 0),
                        title_fr=st['fr'].get('title', ''), description_fr=st['fr'].get('description', ''),
                        title_en=st['en'].get('title', ''), description_en=st['en'].get('description', ''),
                        title_ar=st['ar'].get('title', ''), description_ar=st['ar'].get('description', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"ProcessSteps : {len(plan['process'])} importée(s)."))

            if 'stats' in plan:
                SiteStat.objects.all().delete()
                for s in plan['stats']:
                    SiteStat.objects.create(
                        value=s.get('value', ''), suffix=s.get('suffix', ''), order=s.get('order', 0),
                        label_fr=s['fr'].get('label', ''), label_en=s['en'].get('label', ''),
                        label_ar=s['ar'].get('label', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"SiteStats : {len(plan['stats'])} importée(s)."))

            if 'skills' in plan:
                SkillBar.objects.all().delete()
                for sk in plan['skills']:
                    SkillBar.objects.create(
                        label_fr=sk['fr'].get('label', ''), label_en=sk['en'].get('label', ''),
                        label_ar=sk['ar'].get('label', ''),
                        percentage=sk.get('percentage', 0), order=sk.get('order', 0),
                    )
                self.stdout.write(self.style.SUCCESS(f"SkillBars : {len(plan['skills'])} importée(s)."))

            if 'settings' in plan:
                ss = SiteSettings.load()
                filled, kept = [], []

                def _default(attr):
                    try:
                        d = SiteSettings._meta.get_field(attr).default
                        return d() if callable(d) else d
                    except Exception:
                        return ''

                def _should_set(attr, value):
                    current = getattr(ss, attr, None)
                    if attr in ('latitude', 'longitude'):
                        try:
                            value = float(str(value).replace(',', '.'))
                        except (TypeError, ValueError):
                            return False, None
                        return (current is None), value
                    if current in (None, ''):
                        return True, value
                    # Prérempli par le client (différent du défaut du modèle) : conservé.
                    # Égal au défaut : jamais personnalisé -> le TXT prend le dessus.
                    return (current == _default(attr)), value

                for field, value in plan['settings']['non_trad'].items():
                    ok, cleaned = _should_set(field, value)
                    if ok:
                        setattr(ss, field, cleaned)
                        filled.append(field)
                    else:
                        kept.append(field)
                for lang in LANGS:
                    for field, value in plan['settings'][lang].items():
                        attr = f'{field}_{lang}'
                        ok, cleaned = _should_set(attr, value)
                        if ok:
                            setattr(ss, attr, cleaned)
                            filled.append(attr)
                        else:
                            kept.append(attr)
                ss.save()
                self.stdout.write(self.style.SUCCESS(f'SiteSettings : {len(filled)} champ(s) rempli(s).'))
                if kept:
                    self.stdout.write(f'  (conservés, déjà remplis : {len(kept)})')

            if 'career_page' in plan:
                cp = CareerPage.load()
                filled = []
                for lang in LANGS:
                    for field, value in plan['career_page'][lang].items():
                        attr = f'{field}_{lang}'
                        current = getattr(cp, attr, None)
                        if current in (None, ''):
                            setattr(cp, attr, value)
                            filled.append(attr)
                        else:
                            try:
                                d = CareerPage._meta.get_field(field).default
                                default = d() if callable(d) else d
                            except Exception:
                                default = ''
                            if current == default:
                                setattr(cp, attr, value)
                                filled.append(attr)
                cp.save()
                self.stdout.write(self.style.SUCCESS(f'CareerPage : {len(filled)} champ(s) rempli(s).'))

            if 'hiring' in plan:
                HiringStep.objects.all().delete()
                for h in plan['hiring']:
                    HiringStep.objects.create(
                        order=_to_int(h['nontrad'].get('order')),
                        title_fr=h['fr'].get('title', ''), description_fr=h['fr'].get('description', ''),
                        title_en=h['en'].get('title', ''), description_en=h['en'].get('description', ''),
                        title_ar=h['ar'].get('title', ''), description_ar=h['ar'].get('description', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"HiringSteps : {len(plan['hiring'])} importée(s)."))

            if 'perks' in plan:
                Perk.objects.all().delete()
                for pk in plan['perks']:
                    icon = pk['nontrad'].get('icon', '')
                    if _is_note(icon) or _is_placeholder(icon):
                        icon = ''
                    Perk.objects.create(
                        icon=icon or 'star', order=_to_int(pk['nontrad'].get('order')),
                        title_fr=pk['fr'].get('title', ''), description_fr=pk['fr'].get('description', ''),
                        title_en=pk['en'].get('title', ''), description_en=pk['en'].get('description', ''),
                        title_ar=pk['ar'].get('title', ''), description_ar=pk['ar'].get('description', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"Perks : {len(plan['perks'])} importée(s)."))

            if 'timeline' in plan:
                TimelineEvent.objects.all().delete()
                for ev in plan['timeline']:
                    year = ev['nontrad'].get('year', '')
                    if _is_note(year) or _is_placeholder(year):
                        year = ''
                    TimelineEvent.objects.create(
                        year=year, order=_to_int(ev['nontrad'].get('order')),
                        title_fr=ev['fr'].get('title', ''), description_fr=ev['fr'].get('description', ''),
                        title_en=ev['en'].get('title', ''), description_en=ev['en'].get('description', ''),
                        title_ar=ev['ar'].get('title', ''), description_ar=ev['ar'].get('description', ''),
                    )
                self.stdout.write(self.style.SUCCESS(f"TimelineEvents : {len(plan['timeline'])} importée(s)."))

            if 'legals' in plan:
                for p in plan['legals']:
                    page, _ = LegalPage.objects.update_or_create(
                        page_type=p['page_type'],
                        defaults={
                            'version_number': p['version'] or '1.0',
                            'last_updated': p['last_updated'] or date.today(),
                            'title_fr': p['fr'].get('title', ''), 'subtitle_fr': p['fr'].get('subtitle', ''),
                            'description_fr': p['fr'].get('description', ''), 'intro_fr': p['fr'].get('intro', ''),
                            'title_en': p['en'].get('title', ''), 'subtitle_en': p['en'].get('subtitle', ''),
                            'description_en': p['en'].get('description', ''), 'intro_en': p['en'].get('intro', ''),
                            'title_ar': p['ar'].get('title', ''), 'subtitle_ar': p['ar'].get('subtitle', ''),
                            'description_ar': p['ar'].get('description', ''), 'intro_ar': p['ar'].get('intro', ''),
                        },
                    )
                    page.articles.all().delete()
                    for a in p['articles']:
                        LegalArticle.objects.create(
                            page=page, number=a['number'], order=a['order'],
                            title_fr=a['fr'].get('title', ''), content_fr=a['fr'].get('content', ''),
                            title_en=a['en'].get('title', ''), content_en=a['en'].get('content', ''),
                            title_ar=a['ar'].get('title', ''), content_ar=a['ar'].get('content', ''),
                        )
                n_art = sum(len(p['articles']) for p in plan['legals'])
                self.stdout.write(self.style.SUCCESS(
                    f"LegalPages : {len(plan['legals'])} page(s), {n_art} article(s)."))

            if 'posts' in plan:
                for p in plan['posts']:
                    slug = p['slug'] or slugify(p['fr'].get('title', '') or 'article')
                    Post.objects.update_or_create(
                        slug=slug,
                        defaults={
                            'order': p['order'],
                            'title_fr': p['fr'].get('title', ''), 'category_fr': p['fr'].get('category', ''),
                            'author_name_fr': p['fr'].get('author name', ''), 'author_bio_fr': p['fr'].get('author bio', ''),
                            'excerpt_fr': p['fr'].get('excerpt', ''), 'content_fr': p['fr'].get('content', ''),
                            'reading_time_fr': p['fr'].get('reading time', ''), 'tags_fr': p['fr'].get('tags', ''),
                            'title_en': p['en'].get('title', ''), 'category_en': p['en'].get('category', ''),
                            'author_name_en': p['en'].get('author name', ''), 'author_bio_en': p['en'].get('author bio', ''),
                            'excerpt_en': p['en'].get('excerpt', ''), 'content_en': p['en'].get('content', ''),
                            'reading_time_en': p['en'].get('reading time', ''), 'tags_en': p['en'].get('tags', ''),
                            'title_ar': p['ar'].get('title', ''), 'category_ar': p['ar'].get('category', ''),
                            'author_name_ar': p['ar'].get('author name', ''), 'author_bio_ar': p['ar'].get('author bio', ''),
                            'excerpt_ar': p['ar'].get('excerpt', ''), 'content_ar': p['ar'].get('content', ''),
                            'reading_time_ar': p['ar'].get('reading time', ''), 'tags_ar': p['ar'].get('tags', ''),
                        },
                    )
                self.stdout.write(self.style.SUCCESS(f"Posts : {len(plan['posts'])} importée(s)."))

            if 'team' in plan:
                for m in plan['team']:
                    slug = m['slug'] or slugify(m['fr'].get('name', '') or 'membre')
                    member, _ = TeamMember.objects.update_or_create(
                        slug=slug,
                        defaults={
                            'order': m['order'],
                            'experience_years': m['numeric'].get('experience_years', 10),
                            'projects_count': m['numeric'].get('projects_count', 100),
                            'people_led': m['numeric'].get('people_led', 50),
                            'awards_count': m['numeric'].get('awards_count', 5),
                            'email': m['contact'].get('email', ''), 'phone': m['contact'].get('phone', ''),
                            'facebook': m['contact'].get('facebook', ''), 'twitter': m['contact'].get('twitter', ''),
                            'instagram': m['contact'].get('instagram', ''), 'linkedin': m['contact'].get('linkedin', ''),
                            'name_fr': m['fr'].get('name', ''), 'role_fr': m['fr'].get('role', ''),
                            'department_fr': m['fr'].get('department', ''), 'bio_fr': m['fr'].get('bio', ''),
                            'bio_2_fr': m['fr'].get('bio 2', ''), 'quote_fr': m['fr'].get('quote', ''),
                            'skills_fr': m['fr'].get('skills', ''), 'office_fr': m['fr'].get('office', ''),
                            'name_en': m['en'].get('name', ''), 'role_en': m['en'].get('role', ''),
                            'department_en': m['en'].get('department', ''), 'bio_en': m['en'].get('bio', ''),
                            'bio_2_en': m['en'].get('bio 2', ''), 'quote_en': m['en'].get('quote', ''),
                            'skills_en': m['en'].get('skills', ''), 'office_en': m['en'].get('office', ''),
                            'name_ar': m['ar'].get('name', ''), 'role_ar': m['ar'].get('role', ''),
                            'department_ar': m['ar'].get('department', ''), 'bio_ar': m['ar'].get('bio', ''),
                            'bio_2_ar': m['ar'].get('bio 2', ''), 'quote_ar': m['ar'].get('quote', ''),
                            'skills_ar': m['ar'].get('skills', ''), 'office_ar': m['ar'].get('office', ''),
                        },
                    )
                    member.experiences.all().delete()
                    member.certifications.all().delete()
                    # Les 3 onglets listent les mêmes Experience N dans le même ordre :
                    # on fusionne par index (période non traduite -> FR puis EN puis AR).
                    n_exp = max([len(m[lg].get('experiences', [])) for lg in LANGS] + [0])
                    for i in range(n_exp):
                        per = {lg: (m[lg].get('experiences', []) + [{}] * n_exp)[i] for lg in LANGS}

                        def _exp(lang, key):
                            return (per[lang].get(lang, {}) or {}).get(key, '')
                        period = (
                            (per['fr'].get('periods', {}) or {}).get('fr')
                            or (per['en'].get('periods', {}) or {}).get('en')
                            or (per['ar'].get('periods', {}) or {}).get('ar') or '')
                        TeamExperience.objects.create(
                            member=member, period=period,
                            current=any(bool(per[lg].get('current')) for lg in LANGS),
                            order=per['fr'].get('order', per['en'].get('order', per['ar'].get('order', i))),
                            title_fr=_exp('fr', 'title'), description_fr=_exp('fr', 'description'),
                            title_en=_exp('en', 'title'), description_en=_exp('en', 'description'),
                            title_ar=_exp('ar', 'title'), description_ar=_exp('ar', 'description'),
                        )
                    n_cert = max([len(m[lg].get('certs', [])) for lg in LANGS] + [0])
                    for i in range(n_cert):
                        per = {lg: (m[lg].get('certs', []) + [{}] * n_cert)[i] for lg in LANGS}

                        def _cert(lang):
                            return (per[lang].get(lang, {}) or {}).get('title', '')
                        TeamCertification.objects.create(
                            member=member,
                            order=per['fr'].get('order', per['en'].get('order', per['ar'].get('order', i))),
                            title_fr=_cert('fr'), title_en=_cert('en'), title_ar=_cert('ar'),
                        )
                self.stdout.write(self.style.SUCCESS(f"TeamMembers : {len(plan['team'])} importée(s)."))

        self.stdout.write(self.style.SUCCESS('Import terminé.'))
