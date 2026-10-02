"""
Import des services BS-GROUP depuis un fichier TXT structuré.
Même logique que DIGI-AGENCY : parsing d'un TXT -> remplissage BD (FR/EN/AR via modeltranslation).

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
    return v == '' or v.startswith('(à') or v.startswith('(a`') or 'à renseigner' in v or 'à téléverser' in v


def parse_services_file(path):
    text = Path(path).read_text(encoding='utf-8')
    lines = text.splitlines()

    services = []
    current = None
    section = None  # NON_TRADUITS | FR | EN | AR | FEATURES | BENEFITS | STEPS
    current_feature = None
    current_benefit = None
    current_step = None

    def new_service():
        return {
            'slug': '', 'icon': '', 'order': 0, 'video_url': '',
            'fr': {}, 'en': {}, 'ar': {},
            'features': [], 'benefits': [], 'steps': [],
        }

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Nouveau service
        m_service = re.match(r'SERVICE\s+\d+\s*/\s*\d+\s*[—-]', line)
        if m_service or line.startswith('SERVICE '):
            if current and current.get('slug'):
                services.append(current)
            current = new_service()
            section = None
            current_feature = current_benefit = current_step = None
            continue
        if line.startswith('#') or line.startswith('Légende') or line.startswith('Structure') or line.startswith('BS-GROUP S.A — SERVICES'):
            continue
        if current is None:
            continue

        # Sections
        if line == '--- CHAMPS NON TRADUITS ---':
            section = 'NON_TRADUITS'
            continue
        if line == '--- CHAMPS TRADUITS ---':
            section = None
            continue
        if line in LANG_SECTIONS:
            section = LANG_SECTIONS[line]
            continue
        if line.startswith('--- SERVICE FEATURES'):
            section = 'FEATURES'
            continue
        if line.startswith('--- SERVICE BENEFITS'):
            section = 'BENEFITS'
            continue
        if line.startswith('--- SERVICE STEPS'):
            section = 'STEPS'
            continue

        # --- NON TRADUITS ---
        if section == 'NON_TRADUITS':
            key, value = _split_key_value(line)
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
            # Image / Image 1 / Image 2 / Video cover ignorés (à téléverser via admin)
            continue

        # --- TRADUITS FR/EN/AR ---
        if section in ('fr', 'en', 'ar'):
            key, value = _split_key_value(line)
            field = FIELD_MAP.get(key)
            if field:
                current[section][field] = value
            continue

        # --- FEATURES ---
        if section == 'FEATURES':
            m = re.match(r'\[Feature\s+\d+\]\s*Order\s*:\s*(\d+)', line, re.IGNORECASE)
            if m:
                current_feature = {'order': int(m.group(1)), 'fr': '', 'en': '', 'ar': ''}
                current['features'].append(current_feature)
                continue
            key, value = _split_key_value(line)
            if current_feature is not None and key in ('FR', 'EN', 'AR'):
                current_feature[key.lower()] = value
            continue

        # --- BENEFITS ---
        if section == 'BENEFITS':
            m = re.match(r'\[Benefit\s+\d+\]\s*Icon\s*:\s*(\S+)\s*\|\s*Order\s*:\s*(\d+)', line, re.IGNORECASE)
            if m:
                current_benefit = {
                    'icon': m.group(1).strip(), 'order': int(m.group(2)),
                    'title_fr': '', 'title_en': '', 'title_ar': '',
                    'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                }
                current['benefits'].append(current_benefit)
                continue
            key, value = _split_key_value(line)
            if current_benefit is None:
                continue
            kl = key.lower()
            if kl == 'title fr':
                current_benefit['title_fr'] = value
            elif kl == 'title en':
                current_benefit['title_en'] = value
            elif kl == 'title ar':
                current_benefit['title_ar'] = value
            elif kl == 'description fr':
                current_benefit['desc_fr'] = value
            elif kl == 'description en':
                current_benefit['desc_en'] = value
            elif kl == 'description ar':
                current_benefit['desc_ar'] = value
            continue

        # --- STEPS ---
        if section == 'STEPS':
            m = re.match(r'\[Step\s+\d+\]\s*Number\s*:\s*(\S+)\s*\|\s*Order\s*:\s*(\d+)', line, re.IGNORECASE)
            if m:
                current_step = {
                    'number': m.group(1).strip(), 'order': int(m.group(2)),
                    'title_fr': '', 'title_en': '', 'title_ar': '',
                    'desc_fr': '', 'desc_en': '', 'desc_ar': '',
                }
                current['steps'].append(current_step)
                continue
            key, value = _split_key_value(line)
            if current_step is None:
                continue
            kl = key.lower()
            if kl == 'title fr':
                current_step['title_fr'] = value
            elif kl == 'title en':
                current_step['title_en'] = value
            elif kl == 'title ar':
                current_step['title_ar'] = value
            elif kl == 'description fr':
                current_step['desc_fr'] = value
            elif kl == 'description en':
                current_step['desc_en'] = value
            elif kl == 'description ar':
                current_step['desc_ar'] = value
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
                            help='Supprime tous les services existants avant import.')
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
            self.stdout.write(
                f"  - {s['slug']} (order={s['order']}) "
                f"FR='{s['fr'].get('title', '')[:40]}' | "
                f"feat={len(s['features'])} ben={len(s['benefits'])} steps={len(s['steps'])}"
            )

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry-run : rien écrit en BD.'))
            return

        with transaction.atomic():
            if options['clear']:
                deleted, _ = Service.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'--clear : {deleted} objet(s) supprimé(s).'))

            for data in services:
                slug = data['slug']
                defaults = {
                    'icon': data.get('icon', ''),
                    'order': data.get('order', 0),
                    'video_url': data.get('video_url', ''),
                }
                # Champs traduits -> title_fr, title_en, ...
                for lang in ('fr', 'en', 'ar'):
                    for field, value in data[lang].items():
                        defaults[f'{field}_{lang}'] = value

                service, created = Service.objects.update_or_create(slug=slug, defaults=defaults)

                # Enfants : recréation complète (idempotent)
                service.features.all().delete()
                service.benefits_list.all().delete()
                service.steps.all().delete()

                for f in data['features']:
                    ServiceFeature.objects.create(
                        service=service, order=f['order'],
                        title_fr=f['fr'], title_en=f['en'], title_ar=f['ar'],
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
