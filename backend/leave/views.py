from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsTenantMember
from leave.models import LeaveRequest
from leave.serializers import LeaveRequestSerializer, LeaveReviewActionSerializer
from communication.models import Notification


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["status", "leave_type", "user"]
    search_fields = ["user__first_name", "user__last_name", "reason"]

    def get_queryset(self):
        user = self.request.user
        qs = LeaveRequest.objects.filter(college=user.college).select_related(
            "user", "approved_by"
        )

        if user.role == "STUDENT":
            return qs.filter(user=user)
        elif user.role == "MENTOR":
            if hasattr(user, "faculty_profile"):
                from students.models import MentorAssignment
                student_user_ids = MentorAssignment.objects.filter(
                    mentor=user.faculty_profile, is_active=True
                ).values_list("student__user_id", flat=True)
                return qs.filter(Q(user=user) | Q(user_id__in=student_user_ids))
            return qs.filter(user=user)
        elif user.role == "HOD":
            dept = getattr(getattr(user, "faculty_profile", None), "department", None)
            if dept:
                return qs.filter(
                    Q(user=user)
                    | Q(user__student_profile__department=dept)
                    | Q(user__faculty_profile__department=dept)
                )
            return qs.filter(user=user)
        elif user.role in ["PRINCIPAL", "SUPER_ADMIN"]:
            return qs
        # Standard faculty can only see their own
        return qs.filter(user=user)

    def perform_create(self, serializer):
        req = serializer.save(
            college=self.request.user.college,
            user=self.request.user,
            status="PENDING",
        )

        # Notify mentor or HOD of new leave submission
        if self.request.user.role == "STUDENT" and hasattr(self.request.user, "student_profile"):
            mentor = self.request.user.student_profile.mentor
            if mentor:
                Notification.objects.create(
                    college=req.college,
                    recipient=mentor.user,
                    title=f"Leave request from {self.request.user.get_full_name()}",
                    message=f"{req.days_count} days {req.leave_type}: {req.reason[:80]}",
                    notification_type="LEAVE_STATUS",
                    action_url="/dashboard/leave",
                )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Reviewer approves a leave application."""
        leave_req = self.get_object()
        serializer = LeaveReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave_req.status = "APPROVED"
        leave_req.approved_by = request.user
        leave_req.approval_remarks = serializer.validated_data.get("approval_remarks", "Approved as requested.")
        leave_req.reviewed_at = timezone.now()
        leave_req.save()

        # Send approval notification to applicant
        Notification.objects.create(
            college=leave_req.college,
            recipient=leave_req.user,
            title=f"Your {leave_req.leave_type} has been APPROVED",
            message=f"Remarks: {leave_req.approval_remarks}",
            notification_type="LEAVE_STATUS",
            action_url="/dashboard/leave",
        )

        return Response(LeaveRequestSerializer(leave_req).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reviewer rejects a leave application."""
        leave_req = self.get_object()
        serializer = LeaveReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave_req.status = "REJECTED"
        leave_req.approved_by = request.user
        leave_req.approval_remarks = serializer.validated_data.get("approval_remarks", "Rejected.")
        leave_req.reviewed_at = timezone.now()
        leave_req.save()

        # Send rejection notification to applicant
        Notification.objects.create(
            college=leave_req.college,
            recipient=leave_req.user,
            title=f"Your {leave_req.leave_type} was NOT approved",
            message=f"Reason: {leave_req.approval_remarks}",
            notification_type="LEAVE_STATUS",
            action_url="/dashboard/leave",
        )

        return Response(LeaveRequestSerializer(leave_req).data)
