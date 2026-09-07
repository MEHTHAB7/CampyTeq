from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from colleges.serializers import CollegeSerializer
from .models import User, Role, Permission, AuditLog

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'category', 'description']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source='permissions',
        required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'description', 'permissions', 'permission_ids']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    college = CollegeSerializer(read_only=True)
    college_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'role',
            'status',
            'college',
            'college_id',
            'profile_photo_url',
            'is_mfa_enabled',
            'permissions',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_permissions(self, obj):
        return list(obj.get_all_permissions_list())


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'phone',
            'role',
            'status',
            'college',
            'profile_photo_url'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    college = CollegeSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'role',
            'status',
            'college',
            'profile_photo_url',
            'is_mfa_enabled',
            'permissions'
        ]
        read_only_fields = ['id', 'email', 'role', 'status', 'college']

    def get_permissions(self, obj):
        return list(obj.get_all_permissions_list())


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Augments JWT token response with user profile, active college, and permission list."""
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        if not user.is_active or user.status != 'ACTIVE':
            raise serializers.ValidationError({'detail': 'Your account is inactive or suspended.'})

        if user.college and not user.college.is_active:
            raise serializers.ValidationError({'detail': 'Your institutional college subscription is inactive or suspended.'})

        user_data = UserProfileSerializer(user).data
        data['user'] = user_data
        return data


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'action',
            'resource_type',
            'resource_id',
            'ip_address',
            'user_agent',
            'old_values',
            'new_values',
            'timestamp'
        ]
