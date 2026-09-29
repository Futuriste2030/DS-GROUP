#!/bin/sh
# BS GROUP — Entrypoint production (SQLite)
# Exécute migrations, compilemessages, collectstatic, puis lance gunicorn

set -e

echo "=== BS GROUP Entrypoint ==="
echo "ENV: ${DJANGO_SETTINGS_MODULE:-bsgroup.settings}"
echo "DEBUG: ${DEBUG:-False}"

# SQLite : pas d'attente nécessaire, le fichier est local
# (le volume sqlite_data assure la persistance)
mkdir -p /data /app/staticfiles /app/media
if [ ! -w /data ]; then
    echo "ERROR: /data is not writable by $(whoami). Fix on host with:"
    echo "  docker compose run --rm -u root --entrypoint sh web -c \"chown -R appuser:appgroup /data\""
    exit 1
fi

# Migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Compile translations (FR/EN/AR) — polib fallback si gettext absent
echo "Compiling translations..."
python manage.py compilemessages --ignore=venv --ignore=staticfiles 2>/dev/null || python compile_translations.py

# Collect static (idempotent si déjà fait en build)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Créer superuser si variables définies (optionnel, pour premier déploiement)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

echo "=== Starting Gunicorn ==="
exec "$@"