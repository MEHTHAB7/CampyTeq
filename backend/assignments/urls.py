from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, AssignmentSubmissionViewSet

router = DefaultRouter()
router.register(r'submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'', AssignmentViewSet, basename='assignment')

urlpatterns = router.urls
