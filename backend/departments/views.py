from rest_framework import viewsets, permissions, filters
from common.permissions import IsAdminOrPrincipal, IsTenantMember
from .models import Department
from .serializers import DepartmentSerializer, DepartmentDetailSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Departments.
    Tenant-isolated: users only see and interact with departments belonging to their college.
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'email']
    ordering_fields = ['name', 'code', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal(), IsTenantMember()]
        return [permissions.IsAuthenticated(), IsTenantMember()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return DepartmentDetailSerializer
        return DepartmentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Department.objects.none()
        if user.role == 'SUPER_ADMIN':
            return Department.objects.filter(is_deleted=False).select_related('hod__user', 'college')
        return Department.objects.filter(college=user.college, is_deleted=False).select_related('hod__user', 'college')

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'SUPER_ADMIN':
            serializer.save(college=user.college)
        else:
            college_id = self.request.data.get('college_id') or user.college_id
            serializer.save(college_id=college_id)
