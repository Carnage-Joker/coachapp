from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

import logging
from .models import Client, ClientProfile
from .services.profile_normalizer import normalize_client_profile


@receiver(post_save, sender=Client)
def build_profile_on_client_save(sender, instance: Client, created: bool, **kwargs):
    data = normalize_client_profile(instance)
    try:
        obj, _ = ClientProfile.objects.get_or_create(client=instance, defaults={"profile": data})
        if not _:
            obj.profile = data
            obj.save(update_fields=["profile", "updated_at"])
    except Exception as e:
        # Avoid crashing saves due to profile issues; endpoint will auto-create if missing
        logging.getLogger(__name__).warning("Client profile build failed: %s", e)
