from rest_framework import serializers
from accounts.serializers import UserProfileSerializer
from faculty.serializers import FacultySerializer
from academics.serializers import CourseSerializer, BatchSerializer, SemesterSerializer
from departments.serializers import DepartmentSerializer
from .models import Student, Guardian, StudentGuardian, MentorAssignment

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            'id',
            'first_name',
            'last_name',
            'relationship',
            'phone',
            'email',
            'occupation',
            'address',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StudentGuardianSerializer(serializers.ModelSerializer):
    guardian_details = GuardianSerializer(source='guardian', read_only=True)

    class Meta:
        model = StudentGuardian
        fields = ['id', 'student', 'guardian', 'guardian_details', 'is_primary', 'emergency_contact']


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    profile_photo_url = serializers.URLField(source='user.profile_photo_url', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    semester_name = serializers.CharField(source='current_semester.name', read_only=True)
    mentor_name = serializers.CharField(source='mentor.user.get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'student_number',
            'roll_number',
            'full_name',
            'email',
            'phone',
            'profile_photo_url',
            'department',
            'department_name',
            'department_code',
            'course',
            'course_name',
            'course_code',
            'batch',
            'batch_name',
            'current_semester',
            'semester_name',
            'mentor',
            'mentor_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'address',
            'admission_date',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentDetailSerializer(StudentSerializer):
    guardian_relations = StudentGuardianSerializer(many=True, read_only=True)
    mentor_details = FacultySerializer(source='mentor', read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ['guardian_relations', 'mentor_details']


class MentorAssignmentSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.user.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    course_code = serializers.CharField(source='student.course.code', read_only=True)

    class Meta:
        model = MentorAssignment
        fields = [
            'id',
            'mentor',
            'mentor_name',
            'student',
            'student_name',
            'student_roll',
            'course_code',
            'assigned_date',
            'is_active',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'assigned_date', 'created_at']
