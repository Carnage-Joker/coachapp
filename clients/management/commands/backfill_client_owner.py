from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from clients.models import Client


class Command(BaseCommand):
    help = "Backfill Client.user for existing rows. Provide --username or --user-id to select the owner."

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username of the user to assign as owner")
        parser.add_argument("--user-id", type=int, help="User ID to assign as owner")
        parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
        parser.add_argument("--batch-size", type=int, default=500, help="Batch size for updates")
        parser.add_argument("--all", action="store_true", help="Also assign rows that already have an owner (override)")

    def handle(self, *args, **options):
        username = options.get("username")
        user_id = options.get("user_id")
        dry_run = options.get("dry_run")
        batch_size = options.get("batch_size")
        override_all = options.get("all")

        if not username and not user_id:
            raise CommandError("Provide --username or --user-id")

        User = get_user_model()
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CommandError("User not found")

        qs = Client.objects.all()
        if not override_all:
            qs = qs.filter(user__isnull=True)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No clients to update."))
            return

        self.stdout.write(f"Backfilling {total} client(s) -> user={user.id} ({getattr(user, 'username', '')})")
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run only. No changes written."))
            return

        updated = 0
        with transaction.atomic():
            for start in range(0, total, batch_size):
                chunk = qs.order_by("id")[start:start + batch_size]
                updated += chunk.update(user=user)

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} client(s)."))

