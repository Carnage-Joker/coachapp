from django.contrib import admin

from .models import CoachProfile


@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "accepting_athletes", "remote_available", "in_person_available", "updated_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "headline", "specialties")
    list_filter = ("accepting_athletes", "remote_available", "in_person_available", "rate_currency")
