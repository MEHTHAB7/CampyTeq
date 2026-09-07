from rest_framework import serializers
from accounts.serializers import UserProfileSerializer
from .models import Faculty

class FacultySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    profile_photo_url = serializers.URLField(source='user.profile_photo_url', read_only=True)

    class Meta:
        model = Faculty
        fields = [
            'id',
            'user',
            'faculty_number',
            'full_name',
            'email',
            'phone',
            'department',
            'department_name',
            'department_code',
            'designation',
            'qualification',
            'specialization',
            'joining_date',
            'employment_type',
            'status',
            'emergency_contact',
            'bio',
            'profile_photo_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FacultyDetailSerializer(FacultySerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)
    is_hod = serializers.SerializerMethodField()

    class Meta(FacultySerializer.Meta):
        fields = FacultySerializer.Meta.fields + ['user_details', 'is_hod']

    def get_is_hod(self, obj):
        return obj.headed_departments.filter(is_deleted=False).exists()
