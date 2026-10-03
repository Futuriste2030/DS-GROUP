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

Usage:
    python manage.py import_site_content
    python manage.py import_site_content --only faqs features
    python manage.py import_site_content --dry-run
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import FAQ, Feature, ProcessStep, SiteSettings, SiteStat, SkillBar

LANGS = ('fr', 'en', 'ar')
LANG_RE = r'\[(FR|EN|AR)\]'

FILE_DEFAULTS = {
    'faqs': 'faqs.txt',
    'features': 'features.txt',
    'process': 'process_step.txt',
    'stats': 'site_stats.txt',
    'skills': 'skill_bar.txt',
    'settings': 'site_setting.txt',
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


class Command(BaseCommand):
    help = 'Importe les contenus transverses depuis les TXT (faqs, features, process, stats, skills, settings).'

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

        for name, items in plan.items():
            if name == 'settings':
                n_trad = {k: len(v) for k, v in items.items() if k in ('fr', 'en', 'ar')}
                self.stdout.write(f'  - settings : non_trad={len(items["non_trad"])} trad={n_trad}')
            else:
                self.stdout.write(f'  - {name} : {len(items)} entrée(s)')

        # Validation icônes (features + process steps) contre le set Lucide local
        icons_dir = Path(settings.BASE_DIR) / 'static' / 'icons' / 'lucide'
        if icons_dir.is_dir() and ('features' in plan or 'process' in plan):
            available = {f.stem for f in icons_dir.glob('*.svg')}
            used = set()
            for f in plan.get('features', []):
                if f.get('icon'):
                    used.add(f['icon'])
            for st in plan.get('process', []):
                if st.get('icon'):
                    used.add(st['icon'])
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

        self.stdout.write(self.style.SUCCESS('Import terminé.'))
