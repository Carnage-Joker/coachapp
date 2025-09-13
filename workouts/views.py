from rest_framework import views, permissions, status
from rest_framework.response import Response

from .services.generation import generate_session, generate_plan, SessionParams


class GenerateWorkoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data or {}
        try:
            params = SessionParams(
                goal=data.get("goal") or "General Fitness",
                duration_min=int(data.get("duration_min") or data.get("duration") or 50),
                fitness_level=data.get("fitness_level") or "Intermediate",
                equipment=list(data.get("equipment") or []),
                target_muscles=list(data.get("target_muscles") or []),
                intensity=data.get("intensity"),
                primary_count=(int(data.get("primary_count")) if str(data.get("primary_count", "")).isdigit() else None),
                accessory_count=(int(data.get("accessory_count")) if str(data.get("accessory_count", "")).isdigit() else None),
            )
        except Exception as e:
            return Response({"detail": f"Invalid input: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        session = generate_session(params)
        return Response(session)


class GeneratePlanView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data or {}
        try:
            plan = generate_plan(data)
        except Exception as e:
            return Response({"detail": f"Invalid input: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(plan)
