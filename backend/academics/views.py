from datetime import datetime
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Course, Batch, Semester, Subject, FacultySubject, TimetableEntry
from .serializers import (
    CourseSerializer,
    BatchSerializer,
    SemesterSerializer,
    SubjectSerializer,
    FacultySubjectSerializer,
    TimetableEntrySerializer,
)

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'department__name']
    ordering_fields = ['name', 'code', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Course.objects.none()

        qs = Course.objects.filter(is_deleted=False).select_related('department', 'college').prefetch_related('batches')
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


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'course__name', 'course__code']
    ordering_fields = ['start_date', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Batch.objects.none()

        qs = Batch.objects.filter(is_deleted=False).select_related('course', 'college').prefetch_related('semesters')
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

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


class SemesterViewSet(viewsets.ModelViewSet):
    serializer_class = SemesterSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['semester_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Semester.objects.none()

        qs = Semester.objects.filter(is_deleted=False).select_related('batch__course', 'college')
        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)

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


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'course__code']
    ordering_fields = ['semester_number', 'code', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Subject.objects.none()

        qs = Subject.objects.filter(is_deleted=False).select_related('course', 'department', 'college')
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

        sem_num = self.request.query_params.get('semester')
        if sem_num:
            qs = qs.filter(semester_number=sem_num)

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


class FacultySubjectViewSet(viewsets.ModelViewSet):
    serializer_class = FacultySubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return FacultySubject.objects.none()

        qs = FacultySubject.objects.filter(is_deleted=False).select_related(
            'subject', 'faculty__user', 'batch', 'college'
        )
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)

        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)

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


class TimetableEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableEntrySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['day_of_week', 'start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return TimetableEntry.objects.none()

        qs = TimetableEntry.objects.filter(is_deleted=False).select_related(
            'course', 'batch', 'semester', 'subject', 'faculty__user', 'college'
        )

        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)

        day = self.request.query_params.get('day_of_week')
        if day:
            qs = qs.filter(day_of_week=day)

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

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Returns today's classes tailored to the authenticated student or faculty member."""
        user = request.user
        today_weekday = datetime.now().isoweekday()
        # Fallback to Monday (1) if Sunday (7)
        day_query = 1 if today_weekday > 6 else today_weekday

        qs = self.get_queryset().filter(day_of_week=day_query)

        if user.role == 'STUDENT':
            student_profile = getattr(user, 'student_profile', None)
            if student_profile:
                qs = qs.filter(batch=student_profile.batch)
        elif user.role in ['FACULTY', 'HOD', 'MENTOR']:
            faculty_profile = getattr(user, 'faculty_profile', None)
            if faculty_profile:
                qs = qs.filter(faculty=faculty_profile)

        serializer = self.get_serializer(qs, many=True)
        return Response({
            'day_of_week': day_query,
            'classes': serializer.data,
            'total': qs.count()
        })
