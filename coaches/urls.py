from rest_framework.routers import DefaultRouter

from .views import CoachProfileViewSet

router = DefaultRouter()
router.register(r"", CoachProfileViewSet, basename="coach-profiles")

urlpatterns = router.urls
