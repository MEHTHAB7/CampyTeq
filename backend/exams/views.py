from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Exam, ExamSubject, Result
from .serializers import ExamSerializer, ExamSubjectSerializer, ResultSerializer

class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'batch__name', 'semester__name']
    ordering_fields = ['start_date', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Exam.objects.none()

        qs = Exam.objects.filter(is_deleted=False).select_related('batch', 'semester', 'college').prefetch_related('exam_subjects__subject')

        # Students only see exams that are published or scheduled for their batch
        if user.role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                qs = qs.filter(batch=student_profile.batch)

        if user.role == 'SUPER_ADMIN':
            return qs
        return qs.filter(college=user.college)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'SUPER_ADMIN':
            serializer.save(college=user.college)
        else:
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Authorizes publishing exam results to students and parents."""
        exam = self.get_object()
        exam.is_published = True
        exam.status = 'COMPLETED'
        exam.save()
        return Response({'message': f"Results for '{exam.name}' have been officially published."})


class ExamSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ExamSubject.objects.none()

        qs = ExamSubject.objects.select_related('exam', 'subject')
        exam_id = self.request.query_params.get('exam_id')
        if exam_id:
            qs = qs.filter(exam_id=exam_id)

        if user.role == 'SUPER_ADMIN':
            return qs
        return qs.filter(exam__college=user.college)


class ResultViewSet(viewsets.ModelViewSet):
    """
    Manages marks and student results.
    Enforces privacy: students and parents ONLY receive results for published exams.
    """
    serializer_class = ResultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__roll_number', 'student__user__first_name', 'student__user__last_name', 'exam_subject__subject__code']
    ordering_fields = ['marks_obtained', 'student__roll_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Result.objects.none()

        qs = Result.objects.filter(is_deleted=False).select_related(
            'exam_subject__exam', 'exam_subject__subject', 'student__user', 'college'
        )

        if user.role == 'STUDENT':
            # Strict rule: student only sees their own marks AND ONLY if exam is published
            return qs.filter(
                student__user=user,
                exam_subject__exam__is_published=True
            )

        if user.role == 'PARENT':
            # Parent only sees linked wards' results AND only if published
            return qs.filter(
                student__guardian_relations__guardian__user=user,
                exam_subject__exam__is_published=True
            )

        exam_id = self.request.query_params.get('exam_id')
        if exam_id:
            qs = qs.filter(exam_subject__exam_id=exam_id)

        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)

        if user.role == 'SUPER_ADMIN':
            return qs
        return qs.filter(college=user.college)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'SUPER_ADMIN':
            serializer.save(college=user.college, entered_by=user)
        else:
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id, entered_by=user)
