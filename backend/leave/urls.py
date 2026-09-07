from rest_framework.routers import DefaultRouter
from leave.views import LeaveRequestViewSet

router = DefaultRouter()
router.register(r"requests", LeaveRequestViewSet, basename="leave-requests")

urlpatterns = router.urls
