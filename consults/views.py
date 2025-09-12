from __future__ import annotations

from typing import Any, Dict

from django.utils.timezone import now
from rest_framework import viewsets, permissions, status, parsers, throttling
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Consult, Message, Assessment
from .serializers import ConsultSerializer, MessageSerializer
from .services import ai_respond
from django.conf import settings
import logging
import base64
import tempfile
from typing import Optional
import os
import uuid
from pathlib import Path
import hmac
import hashlib
import time
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from clients.services.profile_normalizer import normalize_client_profile
from clients.services.generator import generate_week_plan
from types import SimpleNamespace


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class IsPremium(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        require = getattr(settings, "CONSULTS_REQUIRE_PREMIUM", False)
        if not require:
            return True
        # Simple heuristic: staff or in 'premium' group qualifies
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True
        try:
            return request.user.groups.filter(name="premium").exists()
        except Exception:
            return False


class ConsultViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultSerializer
    permission_classes = [permissions.IsAuthenticated, IsPremium]
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'consults'
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        qs = Consult.objects.filter(user=self.request.user).order_by("-created_at")
        client_id = self.request.query_params.get("client_id")
        if client_id:
            qs = qs.filter(client_id=client_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="messages")
    def list_messages(self, request, pk=None):
        consult = self.get_object()
        qs = consult.messages.all().order_by("created_at")
        return Response(MessageSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="messages", throttle_classes=[throttling.ScopedRateThrottle], throttle_scope='llm')
    def post_message(self, request, pk=None):
        consult = self.get_object()
        text = (request.data or {}).get("text")
        if not text:
            return Response({"detail": "Provide text."}, status=status.HTTP_400_BAD_REQUEST)

        user_msg = Message.objects.create(consult=consult, role="user", text=text)

        # Build chat history for the AI, with optional client profile context
        history = []
        if getattr(consult, "client_id", None):
            try:
                prof = normalize_client_profile(consult.client)
                history.append({"role": "system", "content": f"Client profile context: {prof}"})
            except Exception as e:
                logging.getLogger(__name__).warning("Profile context inject failed: %s", e)
        history.extend(
            {"role": m.role, "content": m.text}
            for m in consult.messages.all().order_by("created_at")
        )
        result = ai_respond(history)

        # Persist assistant reply
        assistant = Message.objects.create(
            consult=consult,
            role="assistant",
            text=result.get("text", ""),
            metadata={"tool_runs": result.get("tool_runs")},
        )

        # Optional: if the assistant produced a recognizable plan JSON, store it
        plan_payload: Dict[str, Any] | None = None
        try:
            # Heuristic: if reply contains a fenced JSON block, attempt to parse
            txt = result.get("text", "")
            if "{" in txt and "}" in txt:
                start = txt.index("{")
                end = txt.rindex("}") + 1
                plan_payload = __import__("json").loads(txt[start:end])
        except Exception as e:
            logging.getLogger(__name__).debug("Assistant JSON parse failed: %s", e)
            plan_payload = None

        if plan_payload and isinstance(plan_payload, dict):
            Assessment.objects.update_or_create(
                consult=consult,
                defaults={
                    "summary": plan_payload.get("summary", ""),
                    "plan": plan_payload.get("plan"),
                    "assistant_message": assistant.text,
                    "generated_at": now(),
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini",
                    "llm_response": result.get("raw"),
                    "used_llm": True,
                },
            )

        return Response(
            {
                "message": MessageSerializer(assistant).data,
                "tool_runs": result.get("tool_runs"),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="generate")
    def generate(self, request, pk=None):
        """
        Generate an assessment for this consult. If a client is linked, use their normalized
        profile to build a week plan; otherwise fall back to defaults. Optionally accepts:
        - use_llm (bool)          -> included in response metadata
        - session_length_min (int)-> overrides session length for generation
        Response includes a lightweight summary and a plan shaped for the assessment page.
        """
        consult = self.get_object()
        data = request.data or {}
        use_llm = bool(data.get("use_llm"))
        try:
            sess_len = int(data.get("session_length_min")) if data.get("session_length_min") is not None else None
        except Exception as e:
            logging.getLogger(__name__).debug("Invalid session_length_min: %s", e)
            sess_len = None

        # Build a generation profile
        profile = None
        if getattr(consult, "client_id", None):
            try:
                profile = normalize_client_profile(consult.client)
            except Exception as e:
                logging.getLogger(__name__).warning("Profile normalization failed: %s", e)
                profile = None
        if not profile:
            # Safe defaults for ad-hoc consults without a client
            profile = {
                "equipment_allowed": ["Bodyweight", "Dumbbells"],
                "location": "Gym",
                "space_max": "Small",
                "impact_max": "Low",
                "require_knee_friendly": False,
                "require_shoulder_friendly": False,
                "require_back_friendly": False,
                "movement_weights": {
                    "Squat": 1.0,
                    "Hinge": 1.0,
                    "Horizontal Push": 1.0,
                    "Horizontal Pull": 1.0,
                    "Vertical Push": 1.0,
                    "Vertical Pull": 1.0,
                    "Lunge": 1.0,
                    "Core – Brace/Anti-Extension": 1.0,
                    "Carry/Gait": 1.0,
                    "Conditioning": 1.0,
                },
                "days_per_week": 3,
                "session_length_min": 50,
                "target_rpe": "7-9",
                "skill_level": "Intermediate",
                "disliked_exercises": [],
                "liked_exercises": [],
            }
        if isinstance(sess_len, int) and sess_len > 0:
            profile["session_length_min"] = sess_len

        # Client object for display and progressive overload (optional)
        client_like = getattr(consult, "client", None)
        if not client_like:
            client_like = SimpleNamespace(
                preferred_name=(consult.title or "Consult"),
                first_name="",
                last_name="",
                blocks=None,
            )

        # Generate a simple week plan (map of Day -> items[])
        base = generate_week_plan(client_like, profile, save=False) or {}
        days = base.get("plan", {}) if isinstance(base, dict) else {}

        # Transform to assessment-friendly session shape: warmup/main/cooldown
        def to_session(items):
            warmup, main = [], []
            for it in items or []:
                nm = (it.get("notes") or "").lower()
                if nm.startswith("warm-up") or nm.startswith("warmup"):
                    warmup.append({
                        "name": it.get("name") or it.get("exercise") or "Warm-up",
                        "duration_min": 2,
                    })
                else:
                    main.append({
                        "Exercise": it.get("name") or it.get("exercise") or "Exercise",
                        "Default Sets": it.get("sets") or 3,
                        "Default Reps": it.get("reps") or 10,
                        "Est. Time (s)": max(60, int((it.get("rest_s") or 60)) + 30) * int(it.get("sets") or 3),
                    })
            # Simple cooldown placeholder
            cooldown = [
                {"name": "Stretch & Breathing", "duration_min": 5},
            ]
            est_main_min = sum(max(1, round((m.get("Est. Time (s)") or 0) / 60)) for m in main)
            est_total = sum(w.get("duration_min", 0) for w in warmup) + est_main_min + sum(c.get("duration_min", 0) for c in cooldown)
            return {
                "estimated_total_min": est_total,
                "warmup": warmup,
                "main": main,
                "cooldown": cooldown,
            }

        plan_map = {day: to_session(items) for day, items in days.items()}

        summary = (
            f"Generated {len(plan_map)}-day plan"
            + (f" at ~{profile.get('session_length_min')} min/session" if profile.get("session_length_min") else "")
        )

        # Persist/update assessment
        assess, _ = Assessment.objects.update_or_create(
            consult=consult,
            defaults={
                "summary": summary,
                "plan": {"plan": plan_map},
                "generated_at": now(),
                "llm_provider": "openai" if use_llm else "",
                "llm_model": "gpt-4o-mini" if use_llm else "",
                "llm_response": None,
                "used_llm": use_llm,
            },
        )

        return Response(
            {
                "summary": assess.summary,
                "plan": assess.plan,
                "used_llm": assess.used_llm,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="voice", throttle_classes=[throttling.ScopedRateThrottle], throttle_scope='llm')
    def voice(self, request, pk=None):
        consult = self.get_object()
        audio = request.FILES.get("audio")
        if not audio:
            return Response({"detail": "Provide 'audio' file."}, status=status.HTTP_400_BAD_REQUEST)

        transcript_text: Optional[str] = None
        err: Optional[str] = None
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            return Response({"detail": "OpenAI API key not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".bin") as tmp:
                for chunk in audio.chunks():
                    tmp.write(chunk)
                tmp.flush()
                tmp.seek(0)

                try:
                    from openai import OpenAI  # new SDK
                    client = OpenAI(api_key=api_key)
                    resp = client.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=tmp,
                    )
                    transcript_text = getattr(resp, "text", None) or (resp.get("text") if isinstance(resp, dict) else None)
                except Exception as e1:
                    # Legacy SDK fallback
                    try:
                        import openai as openai_legacy  # type: ignore
                        openai_legacy.api_key = api_key
                        tmp.seek(0)
                        resp2 = openai_legacy.Audio.transcribe("whisper-1", tmp)
                        transcript_text = resp2.get("text") if isinstance(resp2, dict) else None
                    except Exception as e2:
                        err = str(e2)
                        logging.getLogger(__name__).warning("Legacy transcription failed: %s", e2)
                if not transcript_text:
                    logging.getLogger(__name__).warning("Transcription via OpenAI SDK failed: %s", e1)
        except Exception as e:
            err = str(e)
            logging.getLogger(__name__).warning("Voice transcript processing error: %s", e)

        if not transcript_text:
            return Response({"detail": "Transcription failed.", "error": err}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Persist user message from transcript
        Message.objects.create(consult=consult, role="user", text=transcript_text, metadata={"source": "voice"})

        # Build chat history and get assistant reply (inject profile if present)
        history = []
        if getattr(consult, "client_id", None):
            try:
                prof = normalize_client_profile(consult.client)
                history.append({"role": "system", "content": f"Client profile context: {prof}"})
            except Exception as e:
                logging.getLogger(__name__).warning("Profile context inject failed: %s", e)
        history.extend({"role": m.role, "content": m.text} for m in consult.messages.all().order_by("created_at"))
        result = ai_respond(history)

        assistant = Message.objects.create(
            consult=consult,
            role="assistant",
            text=result.get("text", ""),
            metadata={"tool_runs": result.get("tool_runs"), "from": "voice"},
        )

        # Optional TTS
        audio_url = None
        tts = str(request.query_params.get("tts", "false")).lower() in ("1", "true", "yes")
        if tts and assistant.text:
            try:
                from openai import OpenAI  # type: ignore
                client = OpenAI(api_key=api_key)
                speech = client.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice="alloy",
                    input=assistant.text,
                    format="mp3",
                )
                audio_bytes = getattr(speech, "content", None)
                if not audio_bytes and hasattr(speech, "to_bytes"):
                    audio_bytes = speech.to_bytes()  # type: ignore
                if isinstance(audio_bytes, (bytes, bytearray)):
                    # Persist and return signed URL
                    name = f"{uuid.uuid4().hex}.mp3"
                    out_dir = Path(settings.MEDIA_ROOT) / "tts"
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / name
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)
                    audio_url = self._signed_tts_url(name, expires_in=300)
            except Exception as e:
                # TTS failure is non-fatal
                logging.getLogger(__name__).warning("TTS generation failed: %s", e)

        return Response(
            {
                "transcript": transcript_text,
                "message": MessageSerializer(assistant).data,
                "tool_runs": result.get("tool_runs"),
                **({"audio_url": audio_url} if audio_url else {}),
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _sign(name: str, exp: int) -> str:
        msg = f"{name}:{exp}".encode("utf-8")
        key = str(settings.SECRET_KEY).encode("utf-8")
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    def _signed_tts_url(self, name: str, expires_in: int = 300) -> str:
        exp = int(time.time()) + int(expires_in)
        sig = self._sign(name, exp)
        base = "/api/consults/tts/" + name
        return f"{base}?e={exp}&s={sig}"


class TTSDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPremium]

    def get(self, request, name: str):
        exp = int(request.query_params.get("e", "0") or 0)
        sig = request.query_params.get("s") or ""
        if not exp or not sig:
            raise Http404
        if exp < int(time.time()):
            raise Http404
        expected = ConsultViewSet._sign(name, exp)
        if not hmac.compare_digest(expected, sig):
            raise Http404
        path = Path(settings.MEDIA_ROOT) / "tts" / name
        if not path.exists():
            raise Http404
        return FileResponse(open(path, "rb"), content_type="audio/mpeg")
