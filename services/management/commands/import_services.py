"""
Import des services BS-GROUP depuis un fichier TXT structuré.
Même logique que DIGI-AGENCY : parsing d'un TXT -> remplissage BD (FR/EN/AR via modeltranslation).

Formats supportés :
- Format compact (VERSION ENRICHIE) : non-traduits sur une ligne avec '|',
  sections [FR]/[EN]/[AR] partielles (champs inchangés omis = conservés en BD),
  Features/Benefits/Steps en lignes compactes.
- Ancien format verbeux (sections '--- ... ---', features/benefits/steps multilignes).

Usage:
    python manage.py import_services
    python manage.py import_services --file services_bs_group.txt
    python manage.py import_services --file services_bs_group.txt --clear
    python manage.py import_services --dry-run
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from services.models import Service, ServiceBenefit, ServiceFeature, ServiceStep


# Mapping labels TXT -> champs modèle Service
FIELD_MAP = {
    'Title': 'title',
    'Excerpt': 'excerpt',
    'Category': 'category',
    'Timeline': 'timeline',
    'Team size': 'team_size',
    'Warranty': 'warranty',
    'Intro': 'intro',
    'Approach title': 'approach_title',
    'Approach': 'approach',
    'Includes title': 'includes_title',
    'Includes description': 'includes_description',
    'Image 1 alt': 'image_1_alt',
    'Image 2 alt': 'image_2_alt',
    'Benefits title': 'benefits_title',
    'Benefits description': 'benefits_description',
    'Video cover alt': 'video_cover_alt',
    'Process title': 'process_title',
    'Process description': 'process_description',
}

LANG_SECTIONS = {'[FR]': 'fr', '[EN]': 'en', '[AR]': 'ar'}
LANGS = ('fr', 'en', 'ar')


def _split_key_value(line):
    """Split 'Key : Value' sur le premier ' : '."""
    if ' : ' in line:
        k, v = line.split(' : ', 1)
        return k.strip(), v.strip()
    if ':' in line:
        k, v = line.split(':', 1)
        return k.strip(), v.strip()
    return line.strip(), ''


def _is_placeholder(value):
    v = value.strip().lower()
    return v == '' or v.startswith('(à') or 'à renseigner' in v or 'à téléverser' in v


def _split_trilang(text, sep_pattern=r'\s*\|\s*'):
    """Découpe 'FR ... | EN ... | AR ...' en 3 morceaux (toujours 3, complétés à '')."""
    parts = re.split(sep_pattern, text.strip(), maxsplit=2)
    while len(parts) < 3:
        parts.append('')
    return [p.strip() for p in parts[:3]]


def _strip_lang_prefix(segment, index):
    """Retire un éventuel préfixe 'FR :' / 'EN :' / 'AR :' ; sinon positionnel."""
    m = re.match(r'^(FR|EN|AR)\s*:\s*(.*)$', segment.strip(), re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    return LANGS[index] if index < 3 else 'fr', segment.strip()


def parse_services_file(path):
    text = Path(path).read_text(encoding='utf-8')
    lines = text.splitlines()

    services = []
    current = None
    section = None  # NON_TRADUITS | fr | en | ar | FEATURES | BENEFITS | STEPS
    current_feature = None
    current_benefit = None
    current_step = None

    def new_service():
        return {
            'slug': '', 'icon': '', 'order': 0, 'video_url': None,
            'fr': {}, 'en': {}, 'ar': {},
            'features': [], 'benefits': [], 'steps': [],
        }

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Nouveau service : 'SERVICE 1 / 6 — ...' (nouveau et ancien formats)
        if re.match(r'SERVICE\s+\d+\s*/\s*\d+', line, re.IGNORECASE):
            if current and current.get('slug'):
                services.append(current)
            current = new_service()
            section = None
            current_feature = current_benefit = current_step = None
            continue
        if line.startswith('#') or line.startswith('Légende') or line.startswith('Structure') \
                or line.startswith('BS-GROUP S.A — SERVICES') or line.startswith('Les champs') \
                or line.startswith('Textes enrichis') or line.startswith('Les valeurs de'):
            continue
        if current is None:
            continue

        # --- Marqueurs de section (nouveau + ancien formats) ---
        if line in LANG_SECTIONS:
            section = LANG_SECTIONS[line]
            continue
        low = line.lower()
        if line == '--- CHAMPS NON TRADUITS ---' or low == 'champs non traduits':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = None
            continue
        if line.startswith('--- SERVICE FEATURES') or low == 'features':
            section = 'FEATURES'
            continue
        if line.startswith('--- SERVICE BENEFITS') or low == 'benefits':
            section = 'BENEFITS'
            continue
        if line.startswith('--- SERVICE STEPS') or low == 'steps':
            section = 'STEPS'
            continue

        # --- NON TRADUITS : une ou plusieurs paires 'K : V' séparées par '|' ---
        if section == 'NON_TRADUITS':
            for part in line.split('|'):
                key, value = _split_key_value(part)
                kl = key.lower()
                if kl == 'slug':
                    current['slug'] = value
                elif kl == 'icon':
                    current['icon'] = value
                elif kl == 'order':
                    try:
                        current['order'] = int(value)
                    except ValueError:
                        current['order'] = 0
                elif kl == 'video url':
                    if not _is_placeholder(value):
                        current['video_url'] = value
            # Image / Images / Video cover ignorés (à téléverser via admin)
            continue

        # --- TRADUITS FR/EN/AR (partiel : seuls les champs présents sont MAJ) ---
        if section in LANGS:
            key, value = _split_key_value(line)
            field = FIELD_MAP.get(key)
            if field:
                current[section][field] = value
            continue

        # --- FEATURES ---
        if section == 'FEATURES':
            m = re.match(r'\[Feature\s+(\d+)\]\s*(.*)$', line, re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                rest = m.group(2).strip()
                order = idx - 1
                m_order = re.search(r'Order\s*:\s*(\d+)', rest, re.IGNORECASE)
                if m_order:
                    order = int(m_order.group(1))
                    rest = (rest[:m_order.start()] + rest[m_order.end():]).strip()
                rest = re.sub(r'^[—–-]\s*', '', rest).strip()
                if rest:
                    # Nouveau format compact : 3 segments séparés par '|'
                    feat = {'order': order, 'fr': '', 'en': '', 'ar': ''}
                    for i, seg in enumerate(_split_trilang(rest)):
                        lang, val = _strip_lang_prefix(seg, i)
                        feat[lang] = val
                    current['features'].append(feat)
                    current_feature = feat
                else:
                    # Ancien format : 'Order : N' seul, valeurs FR/EN/AR sur lignes suivantes
                    current_feature = {'order': order, 'fr': '', 'en': '', 'ar': ''}
                    current['features'].append(current_feature)
                continue
            # Ligne de valeur isolée (ancien format multiligne : 'FR : ...')
            key, value = _split_key_value(line)
            if current_feature is not None and key.upper() in ('FR', 'EN', 'AR'):
                current_feature[key.lower()] = value
            continue

        # --- BENEFITS ---
        if section == 'BENEFITS':
            m = re.match(r'\[Benefit\s+(\d+)\]\s*(.*)$', line, re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                rest = m.group(2).strip()
                # Ancien format : 'Icon : xxx | Order : N' (+ lignes Title/Description suivantes)
                m_old = re.match(r'Icon\s*:\s*(\S+)\s*\|\s*Order\s*:\s*(\d+)', rest, re.IGNORECASE)
                if m_old:
                    current_benefit = {
                        'icon': m_old.group(1).strip(), 'order': int(m_old.group(2)),
                        'title_fr': '', 'title_en': '', 'title_ar': '',
                        'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                    }
                    current['benefits'].append(current_benefit)
                    continue
                # Nouveau format compact : 'icon — TitreFR / TitleEN / TitleAR'
                # (le service 1 préfixe l'icône de 'Icon : ...' — on le retire)
                parts = re.split(r'\s*[—–|]\s*', rest, maxsplit=1)
                icon, titles = (parts[0], parts[1]) if len(parts) == 2 else ('', rest)
                icon = re.sub(r'^Icon\s*:\s*', '', icon.strip(), flags=re.IGNORECASE)
                t_fr, t_en, t_ar = _split_trilang(titles, sep_pattern=r'\s*/\s*')
                current_benefit = {
                    'icon': icon.strip(), 'order': idx - 1,
                    'title_fr': t_fr, 'title_en': t_en, 'title_ar': t_ar,
                    'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                }
                current['benefits'].append(current_benefit)
                continue
            key, value = _split_key_value(line)
            if current_benefit is None:
                continue
            kl = key.lower()
            if kl in ('title fr', 'title en', 'title ar'):
                current_benefit['title_' + kl[-2:]] = value
            elif kl in ('description fr', 'description en', 'description ar'):
                current_benefit['desc_' + kl[-2:]] = value
            elif key.upper() in ('FR', 'EN', 'AR'):
                # Nouveau format : lignes 'FR : description...'
                current_benefit['desc_' + key.lower()] = value
            continue

        # --- STEPS ---
        if section == 'STEPS':
            m = re.match(r'\[Step\s+(\d+)\]\s*(.*)$', line, re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                rest = m.group(2).strip()
                # Ancien format : 'Number : 01 | Order : 0'
                m_old = re.match(r'Number\s*:\s*(\S+)\s*\|\s*Order\s*:\s*(\d+)', rest, re.IGNORECASE)
                if m_old:
                    current_step = {
                        'number': m_old.group(1).strip(), 'order': int(m_old.group(2)),
                        'title_fr': '', 'title_en': '', 'title_ar': '',
                        'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                    }
                    current['steps'].append(current_step)
                    continue
                # Nouveau format compact : '01 — TitreFR / TitleEN / TitleAR'
                parts = re.split(r'\s*[—–|]\s*', rest, maxsplit=1)
                number, titles = (parts[0], parts[1]) if len(parts) == 2 else ('%02d' % idx, rest)
                number = re.sub(r'^(Number|Order)\s*:\s*', '', number.strip(), flags=re.IGNORECASE)
                t_fr, t_en, t_ar = _split_trilang(titles, sep_pattern=r'\s*/\s*')
                current_step = {
                    'number': number.strip(), 'order': idx - 1,
                    'title_fr': t_fr, 'title_en': t_en, 'title_ar': t_ar,
                    'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                }
                current['steps'].append(current_step)
                continue
            key, value = _split_key_value(line)
            if current_step is None:
                continue
            kl = key.lower()
            if kl in ('title fr', 'title en', 'title ar'):
                current_step['title_' + kl[-2:]] = value
            elif kl in ('description fr', 'description en', 'description ar'):
                current_step['desc_' + kl[-2:]] = value
            elif key.upper() in ('FR', 'EN', 'AR'):
                current_step['desc_' + key.lower()] = value
            continue

    if current and current.get('slug'):
        services.append(current)
    return services


class Command(BaseCommand):
    help = 'Importe les services depuis un fichier TXT (FR/EN/AR) — logique DIGI-AGENCY.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='services_bs_group.txt',
                            help='Chemin du fichier TXT (relatif BASE_DIR ou absolu).')
        parser.add_argument('--clear', action='store_true',
                            help='Supprime tous les services existants avant import. '
                                 'Déconseillé avec un fichier partiel (champs omis = perdus).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Parse seulement, sans écrire en BD.')

    def handle(self, *args, **options):
        raw_path = options['file']
        p = Path(raw_path)
        if not p.is_absolute():
            p = Path(settings.BASE_DIR) / raw_path
        if not p.exists():
            self.stderr.write(self.style.ERROR(f'Fichier introuvable : {p}'))
            return

        services = parse_services_file(p)
        self.stdout.write(f'Fichier : {p} — {len(services)} service(s) détecté(s).')
        for s in services:
            provided = sorted({*s['fr'], *s['en'], *s['ar']})
            self.stdout.write(
                f"  - {s['slug']} (order={s['order']}, icon={s['icon']}) "
                f"champs={len(provided)} "
                f"feat={len(s['features'])} ben={len(s['benefits'])} steps={len(s['steps'])}"
            )

        # Validation : les icônes doivent exister dans static/icons/lucide,
        # sinon le loader JS les ignore silencieusement (icône invisible).
        icons_dir = Path(settings.BASE_DIR) / 'static' / 'icons' / 'lucide'
        if icons_dir.is_dir():
            available = {f.stem for f in icons_dir.glob('*.svg')}
            used = set()
            for s in services:
                if s.get('icon'):
                    used.add(s['icon'])
                for b in s['benefits']:
                    if b.get('icon'):
                        used.add(b['icon'])
            missing = sorted(used - available)
            if missing:
                self.stdout.write(self.style.WARNING(
                    f"Icônes absentes de static/icons/lucide (invisibles sur le site) : {', '.join(missing)}"))
            else:
                self.stdout.write('Icônes : toutes présentes dans static/icons/lucide.')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry-run : rien écrit en BD.'))
            return

        with transaction.atomic():
            if options['clear']:
                self.stdout.write(self.style.WARNING(
                    '--clear : les champs absents du TXT seront vides après recréation.'))
                deleted, _ = Service.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'--clear : {deleted} objet(s) supprimé(s).'))

            for data in services:
                slug = data['slug']
                service, created = Service.objects.get_or_create(slug=slug)
                # MAJ partielle : seuls les champs présents dans le TXT sont écrasés
                service.icon = data.get('icon') or service.icon
                service.order = data.get('order', service.order)
                if data.get('video_url'):
                    service.video_url = data['video_url']
                for lang in LANGS:
                    for field, value in data[lang].items():
                        setattr(service, f'{field}_{lang}', value)
                service.save()

                # Enfants : recréation complète (le TXT liste toujours tout)
                service.features.all().delete()
                service.benefits_list.all().delete()
                service.steps.all().delete()

                for f in data['features']:
                    ServiceFeature.objects.create(
                        service=service, order=f['order'],
                        title_fr=f.get('fr', ''), title_en=f.get('en', ''), title_ar=f.get('ar', ''),
                    )
                for b in data['benefits']:
                    ServiceBenefit.objects.create(
                        service=service, order=b['order'], icon=b['icon'],
                        title_fr=b['title_fr'], title_en=b['title_en'], title_ar=b['title_ar'],
                        description_fr=b['desc_fr'], description_en=b['desc_en'], description_ar=b['desc_ar'],
                    )
                for st in data['steps']:
                    ServiceStep.objects.create(
                        service=service, order=st['order'], number=st['number'],
                        title_fr=st['title_fr'], title_en=st['title_en'], title_ar=st['title_ar'],
                        description_fr=st['desc_fr'], description_en=st['desc_en'], description_ar=st['desc_ar'],
                    )

                action = 'créé' if created else 'mis à jour'
                self.stdout.write(self.style.SUCCESS(f'Service {slug} {action}.'))

        self.stdout.write(self.style.SUCCESS('Import terminé.'))
