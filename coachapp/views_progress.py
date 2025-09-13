from __future__ import annotations

from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from clients.models import Client, ClientBlock
from consults.models import Consult, Assessment


class ProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        clients_qs = Client.objects.filter(user=user, archived=False)
        consults_qs = Consult.objects.filter(user=user)
        blocks_qs = ClientBlock.objects.filter(client__user=user, client__archived=False)
        assessments_qs = Assessment.objects.filter(consult__user=user)

        def latest_dt(qs, field: str):
            try:
                return qs.order_by(f"-{field}").values_list(field, flat=True).first()
            except Exception:
                return None

        data = {
            "clients": {
                "count": clients_qs.count(),
                "last_updated": latest_dt(clients_qs, "updated_at"),
            },
            "consults": {
                "count": consults_qs.count(),
                "last_updated": latest_dt(consults_qs, "updated_at"),
            },
            "blocks": {
                "count": blocks_qs.count(),
                "last_updated": latest_dt(blocks_qs, "updated_at"),
            },
            "assessments": {
                "count": assessments_qs.count(),
                "last_updated": latest_dt(assessments_qs, "created_at"),
            },
            "generated_at": now(),
        }
        return Response(data)

