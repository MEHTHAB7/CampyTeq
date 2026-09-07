from rest_framework import serializers
from leave.models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    days_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "user",
            "user_name",
            "user_role",
            "leave_type",
            "from_date",
            "to_date",
            "days_count",
            "reason",
            "attachment_url",
            "status",
            "approved_by",
            "approved_by_name",
            "approval_remarks",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["user", "status", "approved_by", "reviewed_at", "created_at"]


class LeaveReviewActionSerializer(serializers.Serializer):
    approval_remarks = serializers.CharField(required=False, allow_blank=True, default="")
