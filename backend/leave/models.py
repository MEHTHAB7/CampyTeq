from django.db import models
from django.utils import timezone
from common.models import TenantModel


class LeaveRequest(TenantModel):
    class LeaveType(models.TextChoices):
        MEDICAL = "MEDICAL", "Medical / Health Leave"
        CASUAL = "CASUAL", "Casual Leave"
        ACADEMIC_DUTY = "ACADEMIC_DUTY", "Duty / Conference Leave"
        PERSONAL = "PERSONAL", "Personal Leave"
        EMERGENCY = "EMERGENCY", "Emergency Leave"

    class LeaveStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.CharField(
        max_length=30,
        choices=LeaveType.choices,
        default=LeaveType.CASUAL,
    )
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    attachment_url = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
    )
    routed_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leave_reviews",
        help_text="The specific reviewer at this hierarchy level assigned to review this request."
    )
    routed_tier = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text="Target approval tier: MENTOR, HOD, or PRINCIPAL."
    )
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
    )
    approval_remarks = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def days_count(self):
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days + 1
        return 1

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.leave_type}) {self.from_date} to {self.to_date} - {self.status}"
