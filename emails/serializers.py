from rest_framework import serializers
from .models import EmailLog


class ExerciseItemSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    exercise = serializers.CharField(required=False, allow_blank=True)
    movement_pattern = serializers.CharField(required=False, allow_blank=True)
    sets = serializers.IntegerField(required=False)
    reps = serializers.IntegerField(required=False)
    rest_s = serializers.IntegerField(required=False, allow_null=True)
    rest = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    equipment = serializers.CharField(required=False, allow_blank=True)


class PlanDaySerializer(serializers.Serializer):
    day = serializers.CharField()
    items = ExerciseItemSerializer(many=True)


class PlanSerializer(serializers.Serializer):
    client = serializers.CharField(required=False, allow_blank=True)
    days = PlanDaySerializer(many=True)


class SendEmailSerializer(serializers.Serializer):
    to = serializers.EmailField()
    subject = serializers.CharField(max_length=255)
    html = serializers.CharField(required=False, allow_blank=True)
    text = serializers.CharField(required=False, allow_blank=True)
    plan = PlanSerializer(required=False)

    def validate(self, attrs):
        if not attrs.get("html") and not attrs.get("text") and not attrs.get("plan"):
            raise serializers.ValidationError("Provide html, text, or plan to generate content.")
        return attrs


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = [
            "id",
            "to_email",
            "subject",
            "body_text",
            "body_html",
            "status",
            "error_message",
            "meta",
            "created_at",
            "sent_at",
        ]
