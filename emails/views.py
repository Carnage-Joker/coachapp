from datetime import datetime
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailLog
from .serializers import EmailLogSerializer, SendEmailSerializer


def plan_to_simple_html(plan: dict) -> str:
    client_name = plan.get("client") or "Plan"

    def item_stats(it: dict) -> str:
        parts = []
        if it.get("sets") is not None:
            parts.append(f"Sets: {it['sets']}")
        if it.get("reps") is not None:
            parts.append(f"Reps: {it['reps']}")
        rest = it.get("rest_s", it.get("rest"))
        if rest is not None:
            parts.append(f"Rest(s): {rest}")
        if it.get("equipment"):
            parts.append(f"Equipment: {it['equipment']}")
        if it.get("notes"):
            parts.append(f"Notes: {it['notes']}")
        return " • ".join(parts)

    sections = []
    for d in plan.get("days", []):
        items_html = []
        for it in d.get("items", []):
            title = it.get("name") or it.get("exercise") or "Exercise"
            stats = item_stats(it)
            stats_html = (
                f"<div style=\"color:#374151;font:400 12px system-ui,Arial;margin-top:4px\">{stats}</div>"
                if stats
                else ""
            )
            items_html.append(
                f"<li style=\"background:#fff;border:1px solid #f1f1f1;border-radius:10px;padding:10px;margin:8px 0\">"
                f"<div style=\"display:flex;justify-content:space-between;align-items:flex-start;gap:8px\">"
                f"<div><div style=\"font:600 14px system-ui,Arial\">{title}</div>{stats_html}</div>"
                f"</div></li>"
            )
        sections.append(
            f"<section style=\"border:1px solid #e5e7eb;border-radius:12px;padding:12px;margin:12px 0\">"
            f"<h2 style=\"font:600 16px system-ui,Arial;margin:0 0 8px\">{d.get('day','')}</h2>"
            f"<ul style=\"list-style:none;padding:0;margin:0\">{''.join(items_html)}</ul>"
            f"</section>"
        )

    styles = "html,body{background:#fff;color:#111;margin:0;padding:16px}" \
             "@media print{section{page-break-inside:avoid;break-inside:avoid}}"
    body = (
        f"<h1 style=\"font:600 18px system-ui,Arial\">Plan for {client_name}</h1>" + "".join(sections)
    )
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\"/>"
        f"<title>Plan - {client_name}</title><style>{styles}</style></head><body>{body}</body></html>"
    )


class SendEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'email_send'

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_email = serializer.validated_data["to"]
        subject = serializer.validated_data["subject"]
        body_html = serializer.validated_data.get("html")
        body_text = serializer.validated_data.get("text", "")
        plan = serializer.validated_data.get("plan")

        if plan and not body_html:
            body_html = plan_to_simple_html(plan)
        if not body_text:
            body_text = "Your plan is attached in HTML format."

        log = EmailLog.objects.create(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html or "",
            status="queued",
            meta={"has_plan": bool(plan)},
        )

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=body_text,
                to=[to_email],
            )
            if body_html:
                msg.attach_alternative(body_html, "text/html")
            msg.send()
            log.status = "sent"
            log.sent_at = now()
            log.save(update_fields=["status", "sent_at"])
            return Response(EmailLogSerializer(log).data, status=status.HTTP_201_CREATED)
        except Exception as e:  # pragma: no cover - best-effort logging
            log.status = "failed"
            log.error_message = str(e)
            log.save(update_fields=["status", "error_message"])
            return Response(EmailLogSerializer(log).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailLogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailLogSerializer
    queryset = EmailLog.objects.all()
