from __future__ import annotations

from django.conf import settings
from django.db import models


class Consult(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # From 0002 migration
    duration_min = models.IntegerField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    use_llm = models.BooleanField(default=False)
    # Link to a Client for context-aware chats (optional)
    client = models.ForeignKey('clients.Client', null=True, blank=True, on_delete=models.SET_NULL, related_name='consults')

    def __str__(self):
        return self.title or f"Consult {self.pk}"


class Assessment(models.Model):
    consult = models.OneToOneField(Consult, on_delete=models.CASCADE, related_name="assessment")
    summary = models.TextField(blank=True)
    plan = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 0002 fields
    assistant_message = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    llm_model = models.CharField(max_length=128, blank=True)
    llm_provider = models.CharField(max_length=128, blank=True)
    llm_response = models.JSONField(null=True, blank=True)
    session_length_min = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, default="generated")
    used_llm = models.BooleanField(default=False)


class Message(models.Model):
    ROLE_CHOICES = [("user", "user"), ("assistant", "assistant"), ("system", "system")]

    consult = models.ForeignKey(Consult, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 0002 field
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
