"""
Purge le HTML stocké en BD dans les champs affichés SANS |safe.

Contexte : CKEditor était appliqué à tous les TextField de l'admin et
stockait des '<p>...</p>' + entités ('&eacute;...'), affichés en brut
par l'auto-escape Django sur toutes les pages détail
(services, blog, projets, team, careers, FAQ...).

La commande applique, champ par champ : html.unescape PUIS strip_tags
(l'ordre compte : '&lt;p&gt;' doit d'abord redevenir '<p>' pour être retiré).
Ne touche JAMAIS aux champs affichés avec |safe (contenu riche voulu) :
  - blog.Post.content
  - projects.Project.description / challenge / solution / scope_description / result
  - main.SiteSettings.address

Usage:
    python manage.py clean_html            # purge + rapport
    python manage.py clean_html --dry-run  # compte seulement
"""
import html as html_module
import re

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags

# (app, modèle) -> champs riches à NE PAS purger (affichés avec |safe).
RICH_FIELDS = {
    ('blog', 'post'): {'content'},
    ('projects', 'project'): {'description', 'challenge', 'solution', 'scope_description', 'result'},
    ('main', 'sitesettings'): {'address'},
}

# Modèles dont les textes s'affichent en brut (auto-escape / linebreaksbr).
TARGETS = [
    ('services', 'Service'), ('services', 'ServiceFeature'),
    ('services', 'ServiceBenefit'), ('services', 'ServiceStep'),
    ('blog', 'Post'),
    ('projects', 'Project'), ('projects', 'ProjectPoint'), ('projects', 'ProjectStep'),
    ('team', 'TeamMember'), ('team', 'TeamExperience'),
    ('team', 'TeamCertification'), ('team', 'Testimonial'),
    ('careers', 'CareerPage'), ('careers', 'Perk'),
    ('careers', 'HiringStep'), ('careers', 'JobOpening'),
    ('main', 'SiteSettings'), ('main', 'FAQ'), ('main', 'Partner'),
    ('main', 'SiteStat'), ('main', 'SkillBar'), ('main', 'ProcessStep'),
    ('main', 'Feature'), ('main', 'TimelineEvent'),
]

TAG_RE = re.compile(r'<[a-zA-Z/!][^>]*>')


def _base_name(field_name):
    return re.sub(r'_(fr|en|ar)$', '', field_name)


def clean_value(value):
    """Unescape PUIS strip tags. Retourne (nouveau_texte, modifié?)."""
    if not isinstance(value, str) or not value:
        return value, False
    if not TAG_RE.search(value) and '&' not in value:
        return value, False
    cleaned = strip_tags(html_module.unescape(value)).strip()
    return cleaned, cleaned != value


class Command(BaseCommand):
    help = 'Purge tags HTML + entités des champs affichés sans |safe.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Compte seulement, ne modifie rien.')

    def handle(self, *args, **options):
        dry = options['dry_run']
        total_rows = total_fields = 0
        with transaction.atomic():
            for app_label, model_name in TARGETS:
                try:
                    model = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stdout.write(f'  - {app_label}.{model_name} : modèle absent, ignoré')
                    continue
                rich = RICH_FIELDS.get((app_label, model_name), set())
                fields = [
                    f for f in model._meta.get_fields()
                    if getattr(f, 'concrete', False)
                    and f.get_internal_type() in ('CharField', 'TextField')
                    and _base_name(f.name) not in rich
                ]
                rows = fields_changed = 0
                for obj in model.objects.all():
                    dirty = False
                    for f in fields:
                        try:
                            val = getattr(obj, f.name)
                        except Exception:
                            continue
                        new_val, changed = clean_value(val)
                        if changed:
                            setattr(obj, f.name, new_val)
                            dirty = True
                            fields_changed += 1
                    if dirty:
                        if not dry:
                            obj.save(update_fields=[f.name for f in fields])
                        rows += 1
                if rows:
                    self.stdout.write(f'  - {app_label}.{model_name} : {rows} ligne(s), {fields_changed} champ(s)')
                    total_rows += rows
                    total_fields += fields_changed
            if dry:
                self.stdout.write(self.style.WARNING(
                    f'Dry-run : {total_rows} ligne(s) / {total_fields} champ(s) à purger.'))
                transaction.set_rollback(True)
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'Purge terminée : {total_rows} ligne(s) / {total_fields} champ(s) nettoyé(s).'))
