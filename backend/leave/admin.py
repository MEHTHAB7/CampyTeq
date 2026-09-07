from django.contrib import admin
from leave.models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "leave_type", "from_date", "to_date", "days_count", "status", "approved_by", "college"]
    list_filter = ["status", "leave_type", "from_date", "college"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "reason"]
