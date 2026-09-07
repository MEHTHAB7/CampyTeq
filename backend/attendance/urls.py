from rest_framework.routers import DefaultRouter
from attendance.views import (
    AttendanceSessionViewSet,
    StudentAttendanceViewSet,
    FacultyAttendanceViewSet,
)

router = DefaultRouter()
router.register(r"sessions", AttendanceSessionViewSet, basename="attendance-sessions")
router.register(r"students", StudentAttendanceViewSet, basename="student-attendance")
router.register(r"faculty", FacultyAttendanceViewSet, basename="faculty-attendance")

urlpatterns = router.urls
