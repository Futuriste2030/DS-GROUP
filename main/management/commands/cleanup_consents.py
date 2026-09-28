from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import CookieConsent


class Command(BaseCommand):
    help = 'Delete cookie consents (and their logs) older than retention (CNIL: 6 months).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=None,
            help='Retention in days (default: settings.CONSENT_RETENTION_DAYS or 182).',
        )
        parser.add_argument('--dry-run', action='store_true', help='Count only, delete nothing.')

    def handle(self, *args, **options):
        days = options['days'] or getattr(settings, 'CONSENT_RETENTION_DAYS', 182)
        cutoff = timezone.now() - timedelta(days=days)
        qs = CookieConsent.objects.filter(updated_at__lt=cutoff)
        count = qs.count()
        if options['dry_run']:
            self.stdout.write(f'{count} consent(s) older than {days} days (dry-run).')
            return
        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} object(s) older than {days} days.'))
