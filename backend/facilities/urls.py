from rest_framework.routers import DefaultRouter
from facilities.views import FacilityViewSet, FacilityBookingViewSet

router = DefaultRouter()
router.register(r"places", FacilityViewSet, basename="facility-places")
router.register(r"bookings", FacilityBookingViewSet, basename="facility-bookings")

urlpatterns = router.urls
