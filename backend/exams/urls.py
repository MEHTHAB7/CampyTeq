from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamSubjectViewSet, ResultViewSet

router = DefaultRouter()
router.register(r'subjects', ExamSubjectViewSet, basename='exam-subject')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'', ExamViewSet, basename='exam')

urlpatterns = router.urls
