#!/usr/bin/env bash
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate

echo "==> Seeding default role accounts (admin, doctor, nurse)..."
python manage.py seed_roles

echo "==> Creating superuser..."
python manage.py shell << 'PYEOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created!")
else:
    print(f"Superuser '{username}' already exists, skipping.")
PYEOF

# ── Member 5: Security scans ──────────────────────────────────────────
echo "==> Running Bandit security scan..."
# Bandit scans all Python files for common security issues.
# -r = recursive, -x = exclude venv folder, -ll = only show medium/high issues
bandit -r . -x ./venv,./staticfiles --severity-level medium --exit-zero || true

echo "==> Running pip-audit vulnerability scan..."
# pip-audit checks all installed packages against known CVE databases.
# --exit-zero means the build won't fail even if warnings are found,
# so the deploy still completes. Remove --exit-zero to make it strict.
pip-audit --exit-zero || true

echo "==> Running Django deployment checks..."
# check --deploy verifies production security settings are correct.
python manage.py check --deploy --fail-level WARNING || true

echo "==> Build complete!"
