from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subject__name', 'subject__code', 'faculty__user__first_name']
    ordering_fields = ['due_date', 'title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Assignment.objects.none()

        qs = Assignment.objects.filter(is_deleted=False).select_related(
            'faculty__user', 'subject', 'batch', 'college'
        )

        if user.role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                qs = qs.filter(batch=student_profile.batch)
        elif user.role in ['FACULTY', 'HOD']:
            faculty_profile = getattr(user, 'faculty_profile', None)
            if faculty_profile and user.role == 'FACULTY':
                qs = qs.filter(faculty=faculty_profile)

        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        if user.role == 'SUPER_ADMIN':
            return qs
        return qs.filter(college=user.college)

    def perform_create(self, serializer):
        user = self.request.user
        faculty = getattr(user, 'faculty_profile', None)
        if user.role != 'SUPER_ADMIN':
            serializer.save(college=user.college, faculty=faculty)
        else:
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return AssignmentSubmission.objects.none()

        qs = AssignmentSubmission.objects.select_related(
            'assignment__subject', 'student__user', 'graded_by__user'
        )

        if user.role == 'STUDENT':
            # Student strictly sees own submissions
            return qs.filter(student__user=user)

        if user.role in ['FACULTY', 'HOD']:
            faculty = getattr(user, 'faculty_profile', None)
            if faculty:
                return qs.filter(assignment__faculty=faculty)

        if user.role == 'SUPER_ADMIN':
            return qs
        return qs.filter(assignment__college=user.college)

    def perform_create(self, serializer):
        user = self.request.user
        student = getattr(user, 'student_profile', None)
        assignment = serializer.validated_data['assignment']

        # Determine late submission status
        is_late = timezone.now() > assignment.due_date
        sub_status = 'LATE' if is_late else 'SUBMITTED'

        serializer.save(student=student, status=sub_status)

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """Allows faculty to award marks and feedback to a submission."""
        submission = self.get_object()
        user = request.user
        faculty = getattr(user, 'faculty_profile', None)

        marks = request.data.get('marks_awarded')
        feedback = request.data.get('feedback', '')

        if marks is None:
            return Response({'detail': 'marks_awarded is required.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.marks_awarded = marks
        submission.feedback = feedback
        submission.status = 'GRADED'
        submission.graded_by = faculty
        submission.graded_at = timezone.now()
        submission.save()

        return Response(AssignmentSubmissionSerializer(submission).data)
