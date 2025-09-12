from django.db import models


class EmailLog(models.Model):
    STATUS_CHOICES = (
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body_text = models.TextField(blank=True, default="")
    body_html = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="queued")
    error_message = models.TextField(blank=True, default="")
    meta = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.to_email} - {self.subject} ({self.status})"
