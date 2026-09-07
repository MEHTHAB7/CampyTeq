from rest_framework import serializers
from .models import StudentAIAnalysis
from students.models import Student


class StudentAIAnalysisSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_number = serializers.CharField(source='student.student_number', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    department_name = serializers.CharField(source='student.department.name', read_only=True)
    department_code = serializers.CharField(source='student.department.code', read_only=True)
    batch_name = serializers.CharField(source='student.batch.name', read_only=True)
    semester_number = serializers.IntegerField(source='student.current_semester.semester_number', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = StudentAIAnalysis
        fields = [
            'id', 'student', 'student_name', 'student_number', 'roll_number',
            'department_name', 'department_code', 'batch_name', 'semester_number',
            'risk_level', 'score', 'analysis_type', 'attendance_rate',
            'missing_assignments_count', 'average_marks_percentage',
            'leave_days_count', 'key_risk_drivers', 'suggested_interventions',
            'input_snapshot', 'is_latest', 'generated_at',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at',
            'review_notes', 'review_action_taken',
        ]
        read_only_fields = [
            'id', 'score', 'risk_level', 'attendance_rate',
            'missing_assignments_count', 'average_marks_percentage',
            'leave_days_count', 'key_risk_drivers', 'suggested_interventions',
            'input_snapshot', 'is_latest', 'generated_at',
            'reviewed_by', 'reviewed_at',
        ]


class ReviewRiskAnalysisSerializer(serializers.Serializer):
    """Payload submitted by Mentor or HOD to review an early-warning analysis."""
    review_notes = serializers.CharField(min_length=5, required=True)
    review_action_taken = serializers.ChoiceField(
        choices=StudentAIAnalysis.REVIEW_ACTION_CHOICES,
        required=True
    )


class EvaluateStudentSerializer(serializers.Serializer):
    """Payload to trigger on-demand AI risk analysis."""
    student_id = serializers.CharField(required=False)
    department_id = serializers.CharField(required=False)
