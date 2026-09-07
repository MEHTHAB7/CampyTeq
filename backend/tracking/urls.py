from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngestDetectionView,
    DetectionEventViewSet,
    StudentLastSeenView,
    TrackingAuditLogViewSet,
    BiometricProfileViewSet,
)

router = DefaultRouter()
router.register(r'detections', DetectionEventViewSet, basename='tracking-detections')
router.register(r'audit-logs', TrackingAuditLogViewSet, basename='tracking-audit-logs')
router.register(r'biometrics', BiometricProfileViewSet, basename='tracking-biometrics')

urlpatterns = [
    path('ingest/', IngestDetectionView.as_view(), name='tracking-ingest'),
    path('last-seen/', StudentLastSeenView.as_view(), name='tracking-last-seen'),
    path('', include(router.urls)),
]
