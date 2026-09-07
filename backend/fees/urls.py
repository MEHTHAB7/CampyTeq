from rest_framework.routers import DefaultRouter
from fees.views import (
    FeeCategoryViewSet,
    FeeStructureViewSet,
    StudentInvoiceViewSet,
    PaymentViewSet,
    PaymentReceiptViewSet,
)

router = DefaultRouter()
router.register(r"categories", FeeCategoryViewSet, basename="fee-categories")
router.register(r"structures", FeeStructureViewSet, basename="fee-structures")
router.register(r"invoices", StudentInvoiceViewSet, basename="student-invoices")
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"receipts", PaymentReceiptViewSet, basename="receipts")

urlpatterns = router.urls
