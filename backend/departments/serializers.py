from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    hod_name = serializers.CharField(source='hod.user.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'hod',
            'hod_name',
            'email',
            'phone',
            'status',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentDetailSerializer(DepartmentSerializer):
    total_faculty = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    total_courses = serializers.SerializerMethodField()

    class Meta(DepartmentSerializer.Meta):
        fields = DepartmentSerializer.Meta.fields + ['total_faculty', 'total_students', 'total_courses']

    def get_total_faculty(self, obj):
        return obj.faculty_members.filter(is_deleted=False).count()

    def get_total_students(self, obj):
        return obj.students.filter(is_deleted=False).count()

    def get_total_courses(self, obj):
        return obj.courses.filter(is_deleted=False).count()
