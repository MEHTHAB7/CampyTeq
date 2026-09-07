from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from common.permissions import IsSuperAdmin, IsAdminOrPrincipal, IsTenantMember
from .models import User, Role, Permission, AuditLog
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RoleSerializer,
    PermissionSerializer,
    AuditLogSerializer,
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'detail': 'Current password does not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully.'})


class UserViewSet(viewsets.ModelViewSet):
    """
    Tenant-isolated User management.
    Super Admins can manage all users.
    Principals/Management can manage users belonging to their college.
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrPrincipal()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()

        qs = User.objects.filter(is_deleted=False).select_related('college').prefetch_related('custom_roles')

        if user.role == 'SUPER_ADMIN':
            college_filter = self.request.query_params.get('college_id')
            if college_filter:
                qs = qs.filter(college_id=college_filter)
            return qs

        # Tenant isolation: strictly filter to user's college
        return qs.filter(college_id=user.college_id)

    def perform_create(self, serializer):
        user = self.request.user
        # Enforce tenant college
        if user.role != 'SUPER_ADMIN':
            serializer.save(college=user.college)
        else:
            serializer.save()


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all().prefetch_related('permissions')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrPrincipal]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return AuditLog.objects.all().select_related('user', 'college')
        return AuditLog.objects.filter(college=user.college).select_related('user', 'college')
