from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CameraZoneViewSet, CameraViewSet, CameraStatsView

router = DefaultRouter()
router.register(r'zones', CameraZoneViewSet, basename='camera-zones')
router.register(r'cameras', CameraViewSet, basename='cameras')

urlpatterns = [
    path('stats/', CameraStatsView.as_view(), name='camera-stats'),
    path('', include(router.urls)),
]
