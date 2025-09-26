from typing import Any, List

from rest_framework import serializers

from .models import CoachProfile


class CoachProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CoachProfile
        fields = (
            "id",
            "headline",
            "bio",
            "specialties",
            "credentials",
            "years_experience",
            "remote_available",
            "in_person_available",
            "location_city",
            "location_region",
            "location_country",
            "rate_min",
            "rate_currency",
            "accepting_athletes",
            "website",
            "social_links",
            "created_at",
            "updated_at",
            "full_name",
            "email",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "full_name",
            "email",
        )

    def get_full_name(self, obj: CoachProfile) -> str:
        return (obj.user.get_full_name() or obj.user.email).strip()

    def validate_specialties(self, value: Any) -> List[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        raise serializers.ValidationError("Provide a list of specialties or a comma separated string.")

    def validate_social_links(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        raise serializers.ValidationError("Provide a list of URLs.")
