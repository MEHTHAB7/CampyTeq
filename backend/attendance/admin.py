from django.contrib import admin
from attendance.models import AttendanceSession, StudentAttendance, FacultyAttendance


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ["subject", "semester", "faculty", "date", "start_time", "session_type", "college"]
    list_filter = ["session_type", "date", "college"]
    search_fields = ["subject__name", "subject__code", "topic_covered"]


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "session", "status", "marked_at", "marked_by", "college"]
    list_filter = ["status", "marked_at", "college"]
    search_fields = ["student__roll_number", "student__user__first_name", "student__user__last_name"]


@admin.register(FacultyAttendance)
class FacultyAttendanceAdmin(admin.ModelAdmin):
    list_display = ["faculty", "date", "check_in", "check_out", "working_minutes", "status", "punch_source", "college"]
    list_filter = ["status", "punch_source", "date", "college"]
    search_fields = ["faculty__faculty_number", "faculty__user__first_name", "faculty__user__last_name"]
