from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Student, Guardian, StudentGuardian, MentorAssignment
from .serializers import (
    StudentSerializer,
    StudentDetailSerializer,
    GuardianSerializer,
    StudentGuardianSerializer,
    MentorAssignmentSerializer,
)

class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Students with strict multi-tenant isolation and role scoping:
    - Mentors can only access students assigned to them.
    - Students can only view their own record.
    - Parents can only view their linked wards.
    - Administrators, HODs, and Faculty have college-wide student access.
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'student_number',
        'roll_number',
        'user__first_name',
        'user__last_name',
        'user__email',
        'course__code',
        'course__name',
    ]
    ordering_fields = ['roll_number', 'student_number', 'admission_date', 'user__first_name']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return StudentDetailSerializer
        return StudentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Student.objects.none()

        qs = Student.objects.filter(is_deleted=False).select_related(
            'user', 'department', 'course', 'batch', 'current_semester', 'mentor__user', 'college'
        )

        # Principal access
        if user.role == 'PRINCIPAL':
            if user.college:
                return self._apply_filters(qs.filter(college=user.college))
            return self._apply_filters(qs)

        # Multi-tenant isolation: strictly scope to user's college
        qs = qs.filter(college=user.college)

        # Role-based scoping:
        if user.role == 'STUDENT':
            return qs.filter(user=user)

        if user.role == 'PARENT':
            return qs.filter(guardian_relations__guardian__user=user)

        if user.role == 'MENTOR':
            # Scoped strictly to mentor's assigned cohort
            faculty_profile = getattr(user, 'faculty_profile', None)
            if faculty_profile:
                return self._apply_filters(
                    qs.filter(
                        mentor_assignments__mentor=faculty_profile,
                        mentor_assignments__is_active=True
                    )
                )
            return Student.objects.none()

        return self._apply_filters(qs)

    def _apply_filters(self, qs):
        dept_id = self.request.query_params.get('department_id')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'PRINCIPAL':
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)
        else:
            serializer.save(college=user.college)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Allows a logged-in student to retrieve their own full academic profile."""
        student = Student.objects.filter(user=request.user, is_deleted=False).first()
        if not student:
            return Response({'detail': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentDetailSerializer(student)
        return Response(serializer.data)


class GuardianViewSet(viewsets.ModelViewSet):
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PRINCIPAL':
            if user.college:
                return Guardian.objects.filter(college=user.college, is_deleted=False)
            return Guardian.objects.filter(is_deleted=False)
        return Guardian.objects.filter(college=user.college, is_deleted=False)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'PRINCIPAL':
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)
        else:
            serializer.save(college=user.college)


class MentorAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = MentorAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        user = self.request.user
        qs = MentorAssignment.objects.filter(is_deleted=False).select_related(
            'mentor__user', 'student__user', 'student__course', 'college'
        )
        if user.role == 'PRINCIPAL':
            if user.college:
                return qs.filter(college=user.college)
            return qs

        qs = qs.filter(college=user.college)
        if user.role == 'MENTOR':
            faculty = getattr(user, 'faculty_profile', None)
            if faculty:
                return qs.filter(mentor=faculty)
            return MentorAssignment.objects.none()

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'PRINCIPAL':
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)
        else:
            serializer.save(college=user.college)
