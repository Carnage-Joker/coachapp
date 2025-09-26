from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import serializers


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

    def validate_email(self, value: str) -> str:
        User = get_user_model()
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already registered.")
        return email


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        User = get_user_model()
        email = data["email"]
        password = data["password"]
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        refresh = RefreshToken.for_user(user)
        body = {
            "id": user.pk,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return Response(body, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request: Request) -> Response:
        # Blacklist the provided refresh token to log out the session.
        token = (request.data or {}).get("refresh")
        if not token:
            return Response({"detail": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(token)
            refresh.blacklist()
        except Exception as exc:
            return Response({"detail": "invalid token", "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def get(self, request: Request) -> Response:
        user = request.user
        return Response(
            {
                "id": user.pk,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_200_OK,
        )
