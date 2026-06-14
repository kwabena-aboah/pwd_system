#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# build.sh — Render build script for PWD Management System
# ─────────────────────────────────────────────────────────────
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Seeding disability types, categories..."
python manage.py create_initial_data || true

echo "==> Seeding subscription plans..."
python manage.py create_plans || true

echo "==> Creating demo superuser..."
python manage.py shell << 'PYSHELL'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@pwdms.demo').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@pwdms.demo',
        password='PWDdemo2024!',
        first_name='System',
        last_name='Administrator',
        role='super_admin',
    )
    print("  Demo superuser created: admin@pwdms.demo / PWDdemo2024!")
else:
    print("  Superuser already exists.")
PYSHELL

echo "==> Starting demo trial subscription..."
python manage.py shell << 'PYSHELL'
from apps.subscriptions.models import Plan, Subscription
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()
if not Subscription.objects.filter(status__in=['active','trialing']).exists():
    try:
        plan = Plan.objects.get(tier='standard')
        admin = User.objects.filter(role='super_admin').first()
        today = datetime.date.today()
        Subscription.objects.create(
            tenant_name='Demo District Assembly',
            tenant_email='admin@pwdms.demo',
            plan=plan,
            billing_cycle='monthly',
            status='trialing',
            trial_start=today,
            trial_end=today + datetime.timedelta(days=30),
            managed_by=admin,
        )
        print("  Demo trial subscription created (Standard plan, 30 days).")
    except Exception as e:
        print(f"  Could not create trial: {e}")
else:
    print("  Subscription already exists.")
PYSHELL

echo "==> Build complete!"
