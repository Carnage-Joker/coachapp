from __future__ import annotations

from rest_framework import serializers
from .models import Consult, Message, Assessment
from clients.models import Client


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "role", "text", "created_at", "metadata")
        read_only_fields = ("id", "created_at", "metadata")


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = (
            "summary",
            "plan",
            "created_at",
            "assistant_message",
            "generated_at",
            "llm_model",
            "llm_provider",
            "llm_response",
            "session_length_min",
            "status",
            "used_llm",
        )
        read_only_fields = fields


class ConsultSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    assessment = AssessmentSerializer(read_only=True)
    client = serializers.PrimaryKeyRelatedField(source='client', queryset=Client.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Consult
        fields = (
            "id",
            "title",
            "created_at",
            "updated_at",
            "duration_min",
            "scheduled_at",
            "use_llm",
            "client",
            "messages",
            "assessment",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    # No need for __init__ hack; queryset is set above
