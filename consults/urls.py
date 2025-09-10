from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultViewSet, TTSDownloadView


router = DefaultRouter()
router.register(r'', ConsultViewSet, basename='consults')

urlpatterns = [
    path('', include(router.urls)),
    path('tts/<str:name>/', TTSDownloadView.as_view(), name='consults-tts'),
]
