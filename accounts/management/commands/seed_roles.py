"""
Management command: seed_roles
==============================
Creates default admin, doctor, and nurse accounts on a fresh deployment.
Safe to run multiple times — skips accounts that already exist.

Usage:
    python manage.py seed_roles
    python manage.py seed_roles --password mypassword123

Render build.sh usage:
    python manage.py seed_roles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# Default seed accounts — change passwords via environment variables in production
DEFAULT_ACCOUNTS = [
    {
        'username':    'admin',
        'password':    'Admin@1234',
        'first_name':  'System',
        'last_name':   'Administrator',
        'role':        'admin',
        'is_staff':    True,
        'is_superuser': True,
    },
    {
        'username':    'doctor01',
        'password':    'Doctor@1234',
        'first_name':  'Juan',
        'last_name':   'Dela Cruz',
        'role':        'doctor',
        'is_staff':    False,
        'is_superuser': False,
    },
    {
        'username':    'nurse01',
        'password':    'Nurse@1234',
        'first_name':  'Maria',
        'last_name':   'Santos',
        'role':        'nurse',
        'is_staff':    False,
        'is_superuser': False,
    },
]


class Command(BaseCommand):
    help = (
        'Seeds the database with default admin, doctor, and nurse accounts. '
        'Safe to run multiple times — existing accounts are skipped.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Override the default password for all seeded accounts.',
        )

    def handle(self, *args, **options):
        override_password = options.get('password')
        created_count = 0
        skipped_count = 0

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\n==> Seeding default role accounts...\n'
        ))

        for account in DEFAULT_ACCOUNTS:
            username = account['username']
            password = override_password or account['password']

            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'   SKIP  {username!r} already exists.')
                )
                skipped_count += 1
                continue

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=account['first_name'],
                last_name=account['last_name'],
                role=account['role'],
                is_staff=account['is_staff'],
                is_superuser=account['is_superuser'],
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'   OK    Created {account["role"].upper()!r} → '
                    f'username: {username!r}  password: {password!r}'
                )
            )
            created_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'==> Done. {created_count} account(s) created, {skipped_count} skipped.\n'
        ))

        if created_count > 0:
            self.stdout.write(self.style.WARNING(
                'IMPORTANT: Change these default passwords immediately after first login.'
            ))