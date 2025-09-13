from __future__ import annotations

import datetime as dt
from typing import Dict

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from clients.models import Client


def _parse_map(s: str) -> Dict[str, str]:
    """Parse mapping like "key1:owner1,key2:owner2" into dict.
    Keys are case-insensitive; spaces around keys/values are stripped.
    """
    out: Dict[str, str] = {}
    if not s:
        return out
    for pair in s.split(','):
        if ':' not in pair:
            continue
        k, v = pair.split(':', 1)
        k = (k or '').strip().lower()
        v = (v or '').strip()
        if k and v:
            out[k] = v
    return out


class Command(BaseCommand):
    help = (
        "Reassign or archive clients via heuristics.\n"
        "- Candidates default to owner-null unless --owner-id/--owner-username or --all is provided.\n"
        "- Reassignment precedence: --map-gym, then --map-domain, then --default-owner.\n"
        "- Archive when no reassignment target is found or when --archive-only is set."
    )

    def add_arguments(self, parser):
        # Candidate selection
        parser.add_argument('--owner-null', action='store_true', help='Only process clients with no owner (if DB allows)')
        parser.add_argument('--owner-id', type=int, help='Only process clients owned by this user id')
        parser.add_argument('--owner-username', type=str, help='Only process clients owned by this username')
        parser.add_argument('--all', action='store_true', help='Process all clients (dangerous)')

        # Heuristic parameters
        parser.add_argument('--days-inactive', type=int, default=90, help='Threshold in days to consider inactive by updated_at')
        parser.add_argument('--min-blocks', type=int, default=1, help='Minimum ClientBlock count to consider active')
        parser.add_argument('--require-contact', action='store_true', help='If set, clients without email/phone are archived unless reassigned')

        # Reassignment mapping
        parser.add_argument('--map-gym', type=str, default='', help='Mapping of gym_name to owner (username or id): "Gym A:coach1,Gym B:2"')
        parser.add_argument('--map-domain', type=str, default='', help='Mapping of email domain to owner: "example.com:coach1"')
        parser.add_argument('--default-owner', type=str, help='Fallback owner username or id if no map matched')

        # Behavior flags
        parser.add_argument('--archive', action='store_true', help='Archive candidates with no reassignment target')
        parser.add_argument('--archive-only', action='store_true', help='Do not reassign; only archive matches')
        parser.add_argument('--dry-run', action='store_true', help='Show actions but do not write')
        parser.add_argument('--batch-size', type=int, default=200, help='Batch size for DB writes')

    def handle(self, *args, **opts):
        owner_null = opts['owner_null']
        owner_id = opts.get('owner_id')
        owner_username = opts.get('owner_username')
        process_all = opts['all']
        days_inactive = int(opts['days_inactive'])
        min_blocks = int(opts['min_blocks'])
        require_contact = bool(opts['require_contact'])
        map_gym = _parse_map(opts.get('map_gym') or '')
        map_domain = _parse_map(opts.get('map_domain') or '')
        default_owner_spec = opts.get('default_owner')
        archive_flag = bool(opts['archive'])
        archive_only = bool(opts['archive_only'])
        dry = bool(opts['dry_run'])
        batch_size = int(opts['batch_size'])

        # Build queryset of candidates
        qs = Client.objects.all()
        if owner_null:
            qs = qs.filter(user__isnull=True)
        elif owner_id is not None:
            qs = qs.filter(user_id=owner_id)
        elif owner_username:
            User = get_user_model()
            try:
                u = User.objects.get(username=owner_username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Owner username not found: {owner_username}"))
                return
            qs = qs.filter(user=u)
        elif not process_all:
            self.stderr.write(self.style.WARNING("No candidate filter provided; use --owner-null/--owner-id/--owner-username or --all"))
            return

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No clients matched criteria."))
            return

        # Resolve owner specs in maps to user ids
        User = get_user_model()
        def resolve_owner(spec: str):
            if not spec:
                return None
            spec = spec.strip()
            if spec.isdigit():
                try:
                    return User.objects.get(id=int(spec))
                except User.DoesNotExist:
                    return None
            try:
                return User.objects.get(username=spec)
            except User.DoesNotExist:
                return None

        gym_owner: Dict[str, int] = {}
        for g, spec in map_gym.items():
            u = resolve_owner(spec)
            if u:
                gym_owner[g.lower()] = u.id

        domain_owner: Dict[str, int] = {}
        for d, spec in map_domain.items():
            u = resolve_owner(spec)
            if u:
                domain_owner[d.lower()] = u.id

        default_owner_id = None
        if default_owner_spec:
            u = resolve_owner(default_owner_spec)
            if not u:
                self.stderr.write(self.style.ERROR(f"Default owner not found: {default_owner_spec}"))
                return
            default_owner_id = u.id

        now = timezone.now()
        cutoff = now - dt.timedelta(days=days_inactive)

        def is_active(c: Client) -> bool:
            if getattr(c, 'trains_with_me', False):
                return True
            if getattr(c, 'updated_at', now) and c.updated_at >= cutoff:
                return True
            if c.blocks.count() >= min_blocks:
                return True
            # If profile exists, consider active
            if hasattr(c, 'profile'):
                return True
            return False

        to_reassign: Dict[int, int] = {}  # client_id -> user_id
        to_archive: list[int] = []

        # Iterate and classify
        for c in qs.iterator():
            target_owner_id = None
            if not archive_only:
                g = (c.gym_name or '').strip().lower()
                if g and g in gym_owner:
                    target_owner_id = gym_owner[g]
                elif c.email and '@' in (c.email or ''):
                    dom = c.email.split('@')[-1].lower()
                    if dom in domain_owner:
                        target_owner_id = domain_owner[dom]
                if not target_owner_id and default_owner_id is not None:
                    target_owner_id = default_owner_id

            # If require contact info to stay active and none present, prefer archive
            no_contact = not (c.email or c.phone)
            if (not is_active(c) or (require_contact and no_contact)) and not target_owner_id:
                if archive_flag:
                    to_archive.append(c.id)
                continue

            if target_owner_id and (owner_null or process_all or (owner_id is not None) or owner_username):
                # Only reassign if selection criteria matched and we have a target
                if c.user_id != target_owner_id:
                    to_reassign[c.id] = target_owner_id
            elif archive_flag:
                to_archive.append(c.id)

        self.stdout.write(f"Matched {total} candidates: reassign={len(to_reassign)}, archive={len(to_archive)}")
        if dry:
            self.stdout.write(self.style.WARNING("Dry run; no changes written."))
            return

        # Apply changes
        updated = 0
        archived = 0
        with transaction.atomic():
            # Reassign in batches
            if to_reassign:
                items = list(to_reassign.items())
                for start in range(0, len(items), batch_size):
                    batch = items[start:start + batch_size]
                    ids = [cid for cid, _ in batch]
                    # Group by owner
                    owners: Dict[int, list[int]] = {}
                    for cid, uid in batch:
                        owners.setdefault(uid, []).append(cid)
                    for uid, cids in owners.items():
                        updated += Client.objects.filter(id__in=cids).update(user_id=uid)
            # Archive
            if to_archive:
                for start in range(0, len(to_archive), batch_size):
                    ids = to_archive[start:start + batch_size]
                    archived += Client.objects.filter(id__in=ids).update(archived=True)

        self.stdout.write(self.style.SUCCESS(f"Reassigned {updated}, archived {archived}"))

