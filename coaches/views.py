from typing import Iterable

from django.db import IntegrityError
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from .models import CoachProfile
from .serializers import CoachProfileSerializer


class CoachProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CoachProfileSerializer
    queryset = CoachProfile.objects.select_related("user").all()

    def get_permissions(self) -> Iterable[permissions.BasePermission]:
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        accepting = params.get("accepting")
        if accepting in {"1", "true", "True"}:
            qs = qs.filter(accepting_athletes=True)

        remote = params.get("remote")
        if remote in {"1", "true", "True"}:
            qs = qs.filter(remote_available=True)

        in_person = params.get("in_person")
        if in_person in {"1", "true", "True"}:
            qs = qs.filter(in_person_available=True)

        country = params.get("country")
        if country:
            qs = qs.filter(location_country__iexact=country)

        region = params.get("region")
        if region:
            qs = qs.filter(location_region__icontains=region)

        specialty = params.get("specialty")
        if specialty:
            qs = qs.filter(specialties__icontains=specialty)

        if params.get("mine") in {"1", "true", "True"} and self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)

        return qs

    def perform_create(self, serializer: CoachProfileSerializer) -> None:
        user = self.request.user
        if hasattr(user, "coach_profile"):
            raise ValidationError("Coach profile already exists. Use PATCH to update it.")
        try:
            serializer.save(user=user)
        except IntegrityError as exc:
            raise ValidationError("Unable to create profile.") from exc

    def perform_update(self, serializer: CoachProfileSerializer) -> None:
        instance = serializer.instance
        if instance.user != self.request.user:
            raise ValidationError("You can only update your own coach profile.")
        serializer.save()

    def perform_destroy(self, instance: CoachProfile) -> None:
        if instance.user != self.request.user:
            raise ValidationError("You can only remove your own coach profile.")
        instance.delete()

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:
        profile = getattr(request.user, "coach_profile", None)
        if not profile:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
