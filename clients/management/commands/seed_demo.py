from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from django.db.utils import OperationalError

from clients.models import Client, ClientBlock, ClientEquipment, ClientPreference
from clients.services.profile_normalizer import normalize_client_profile
from clients.services.generator import generate_week_plan
from consults.models import Assessment, Consult, Message
from emails.models import EmailLog
from coaches.models import CoachProfile


class Command(BaseCommand):
    help = "Seed demo data for local walkthroughs (coach, client, consult, and plan)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="trainer@example.com",
            help="Email address for the seeded coach user.",
        )
        parser.add_argument(
            "--password",
            default="demo1234!",
            help="Password for the seeded coach user.",
        )

    def handle(self, *args, **options):
        email: str = options["email"]
        password: str = options["password"]

        user = self._ensure_user(email, password)
        client = self._ensure_client(user)
        block_payload = self._ensure_plan(client)
        consult = self._ensure_consult(user, client, block_payload)
        self._ensure_email_log(client)
        self._ensure_coach_profile(user)

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"Coach login: {email}")
        self.stdout.write(f"Password: {password}")
        self.stdout.write("Hint: browse /intake, /clients, /consults, /workouts/plan, and /progress in the frontend.")

    def _ensure_user(self, email: str, password: str):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": "Demo",
                "last_name": "Coach",
            },
        )
        if not user.email:
            user.email = email
        if created or password:
            user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.save()
        return user

    def _ensure_client(self, user):
        defaults = {
            "first_name": "Jane",
            "last_name": "Doe",
            "preferred_name": "Jane",
            "phone": "555-0100",
            "age_group": "35-44",
            "height_cm": 167,
            "weight_kg": 68,
            "training_age_years": 3,
            "primary_location": "Gym",
            "space_available": "Medium",
            "impact_tolerance": "Moderate",
            "session_length_min": 55,
            "days_per_week": 4,
            "preferred_days": ["Mon", "Wed", "Fri", "Sat"],
            "goals": ["Strength", "Conditioning"],
            "trains_with_me": True,
            "knee_issue": False,
            "shoulder_issue": False,
            "back_issue": False,
            "rpe_familiarity": "Some",
            "power_interest": True,
            "likes_notes": "Enjoys hinges and sled pushes.",
            "dislikes_notes": "Keep plyometrics limited to warm-ups.",
        }
        client, _ = Client.objects.update_or_create(
            user=user,
            email="jane.doe@example.com",
            defaults=defaults,
        )

        ClientPreference.objects.update_or_create(
            client=client,
            kind="Movement Pattern",
            value="Hinge",
            defaults={"sentiment": "Like"},
        )
        ClientPreference.objects.update_or_create(
            client=client,
            kind="Exercise",
            value="Burpees",
            defaults={"sentiment": "Hard No"},
        )

        ClientEquipment.objects.update_or_create(
            client=client,
            category="Dumbbells",
            defaults={"location": "Gym", "details": {"pairs": "5-70 lb"}},
        )
        ClientEquipment.objects.update_or_create(
            client=client,
            category="Resistance Bands",
            defaults={"location": "Gym", "details": {"sets": "light-medium"}},
        )

        return client

    def _table_exists(self, model) -> bool:
        table_name = model._meta.db_table
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        return table_name in tables

    def _ensure_plan(self, client):
        profile = normalize_client_profile(client)
        payload = generate_week_plan(client, profile)
        ClientBlock.objects.update_or_create(
            client=client,
            name="Demo Week 1",
            defaults={"block": payload.get("plan", {})},
        )
        return payload

    def _ensure_consult(self, user, client, payload):
        consult, _ = Consult.objects.get_or_create(
            user=user,
            client=client,
            title="Goal Review",
            defaults={
                "use_llm": True,
                "duration_min": 45,
            },
        )

        if consult.messages.count() == 0:
            Message.objects.create(
                consult=consult,
                role="user",
                text="Can we double-check hinge volume for the next block?",
            )
            Message.objects.create(
                consult=consult,
                role="assistant",
                text="Absolutely. I will keep trap bar work in and add a lighter posterior chain day.",
                metadata={"seed_demo": True},
            )

        Assessment.objects.update_or_create(
            consult=consult,
            defaults={
                "summary": "Balanced four day split with extra posterior chain focus.",
                "plan": payload.get("plan", {}),
                "assistant_message": "Next steps: review hinge pattern cues and monitor recovery on the conditioning day.",
                "generated_at": timezone.now(),
                "status": "generated",
                "used_llm": False,
            },
        )

        return consult

    def _ensure_email_log(self, client):
        if not self._table_exists(EmailLog):
            self.stdout.write(self.style.WARNING("Skipping EmailLog seed; run migrations then rerun seed_demo."))
            return
        to_email = client.email or "jane.doe@example.com"
        try:
            EmailLog.objects.update_or_create(
                to_email=to_email,
                subject="Your Week 1 Training Plan",
                defaults={
                    "body_text": "Attached is the first training week we walked through during your consult.",
                    "body_html": "",
                    "status": "sent",
                    "sent_at": timezone.now(),
                    "meta": {"seed_demo": True},
                },
            )
        except OperationalError:
            self.stdout.write(self.style.WARNING("Unable to seed email log; ensure migrations are applied."))
