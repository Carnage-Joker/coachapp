from django.contrib import admin
from .models import Consult, Message, Assessment


@admin.register(Consult)
class ConsultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "use_llm")
    search_fields = ("title", "user__username", "user__email")
    list_filter = ("use_llm",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "consult", "role", "created_at")
    search_fields = ("text",)
    list_filter = ("role",)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("consult", "generated_at", "status", "used_llm")
    readonly_fields = ("llm_response",)

