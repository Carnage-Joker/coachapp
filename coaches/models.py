from django.conf import settings
from django.db import models
from django.utils import timezone


class CoachProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coach_profile")
    headline = models.CharField(max_length=140, blank=True)
    bio = models.TextField(blank=True)
    specialties = models.JSONField(default=list, blank=True)
    credentials = models.CharField(max_length=255, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    remote_available = models.BooleanField(default=True)
    in_person_available = models.BooleanField(default=False)
    location_city = models.CharField(max_length=120, blank=True)
    location_region = models.CharField(max_length=120, blank=True)
    location_country = models.CharField(max_length=120, blank=True)
    rate_min = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    rate_currency = models.CharField(max_length=3, default="USD")
    accepting_athletes = models.BooleanField(default=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        name = self.user.get_full_name().strip() or self.user.email
        return f"Coach Profile for {name}"
