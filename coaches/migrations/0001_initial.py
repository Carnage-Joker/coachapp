# Generated manually
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CoachProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("headline", models.CharField(blank=True, max_length=140)),
                ("bio", models.TextField(blank=True)),
                ("specialties", models.JSONField(blank=True, default=list)),
                ("credentials", models.CharField(blank=True, max_length=255)),
                ("years_experience", models.PositiveIntegerField(blank=True, null=True)),
                ("remote_available", models.BooleanField(default=True)),
                ("in_person_available", models.BooleanField(default=False)),
                ("location_city", models.CharField(blank=True, max_length=120)),
                ("location_region", models.CharField(blank=True, max_length=120)),
                ("location_country", models.CharField(blank=True, max_length=120)),
                ("rate_min", models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ("rate_currency", models.CharField(default="USD", max_length=3)),
                ("accepting_athletes", models.BooleanField(default=True)),
                ("website", models.URLField(blank=True)),
                ("social_links", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coach_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
    ]
