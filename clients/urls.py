from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet


router = DefaultRouter()
router.register(r'api/clients', ClientViewSet, basename='clients')

urlpatterns = [
    # Router provides: /api/clients/ , /api/clients/<id>/ , /api/clients/<id>/plan/
    path('', include(router.urls)),
]

