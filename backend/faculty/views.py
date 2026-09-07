from rest_framework import viewsets, permissions, filters
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Faculty
from .serializers import FacultySerializer, FacultyDetailSerializer

class FacultyViewSet(viewsets.ModelViewSet):
    """
    CRUD for Faculty members.
    Tenant isolated: results strictly scoped to active college.
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'faculty_number',
        'user__first_name',
        'user__last_name',
        'user__email',
        'department__name',
        'specialization',
    ]
    ordering_fields = ['faculty_number', 'joining_date', 'user__first_name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return FacultyDetailSerializer
        return FacultySerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Faculty.objects.none()

        qs = Faculty.objects.filter(is_deleted=False).select_related('user', 'department', 'college')

        dept_id = self.request.query_params.get('department_id')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

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
