# BS GROUP — Dockerfile production (multi-stage)
# Base: Python 3.12 slim (compatible Django 5.2 + Python 3.14)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps (postgres client, gettext for compilemessages, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Builder: compile translations & collectstatic ----
FROM base AS builder

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Compile translations (FR/EN/AR) — polib already in requirements via django-modeltranslation
RUN python manage.py compilemessages --ignore=venv --ignore=staticfiles || true

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# ---- Runtime: minimal image ----
FROM base AS runtime

# Entrypoint handles migrate + collectstatic + gunicorn
COPY --from=builder /app/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Copy only necessary artifacts from builder
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Static & media volumes (populated at runtime via collectstatic in entrypoint if needed)
# /data holds the SQLite DB (compose: sqlite_data:/data + DATABASE_URL=sqlite:///data/db.sqlite3)
# Pre-create with correct ownership so fresh named volumes inherit appuser ownership
RUN mkdir -p /data /app/staticfiles /app/media && chown -R appuser:appgroup /data /app

USER appuser

EXPOSE 8000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "bsgroup.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]