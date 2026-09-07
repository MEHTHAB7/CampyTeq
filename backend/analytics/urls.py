from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InstitutionalOverviewView,
    AttendanceReportView,
    FinanceReportView,
    AcademicReportView,
    StudentAIAnalysisViewSet,
)

router = DefaultRouter()
router.register(r'ai-risk', StudentAIAnalysisViewSet, basename='analytics-ai-risk')

urlpatterns = [
    path('overview/', InstitutionalOverviewView.as_view(), name='analytics-overview'),
    path('attendance-report/', AttendanceReportView.as_view(), name='analytics-attendance-report'),
    path('finance-report/', FinanceReportView.as_view(), name='analytics-finance-report'),
    path('academic-report/', AcademicReportView.as_view(), name='analytics-academic-report'),
    path('', include(router.urls)),
]
