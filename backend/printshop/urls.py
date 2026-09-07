from rest_framework.routers import DefaultRouter
from printshop.views import PrintPricingViewSet, PrintOrderViewSet

router = DefaultRouter()
router.register(r"pricing", PrintPricingViewSet, basename="print-pricing")
router.register(r"orders", PrintOrderViewSet, basename="print-orders")

urlpatterns = router.urls
