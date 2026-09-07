from rest_framework.routers import DefaultRouter
from payroll.views import SalaryStructureViewSet, PayslipViewSet

router = DefaultRouter()
router.register(r"structures", SalaryStructureViewSet, basename="salary-structures")
router.register(r"payslips", PayslipViewSet, basename="payslips")

urlpatterns = router.urls
