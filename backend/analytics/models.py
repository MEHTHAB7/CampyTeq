from django.db import models
from common.models import TenantModel


class StudentAIAnalysis(TenantModel):
    """
    AI Academic Early-Warning Risk Assessment.
    Provides explainable decision-support risk scoring for mentors & administrators.
    Non-punitive: never alters student enrollment or punitive standing automatically.
    """
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk (0 - 39)'),
        ('MEDIUM', 'Medium Risk (40 - 69)'),
        ('HIGH', 'High Risk (70 - 89)'),
        ('CRITICAL', 'Critical Risk (90 - 100)'),
    ]

    ANALYSIS_TYPE_CHOICES = [
        ('ACADEMIC_EARLY_WARNING', 'Academic Early Warning'),
        ('ATTENDANCE_RISK', 'Attendance Defaulter Risk'),
        ('COMPREHENSIVE', 'Comprehensive Risk Evaluation'),
    ]

    REVIEW_ACTION_CHOICES = [
        ('COUNSELING_SCHEDULED', '1-on-1 Mentorship Counseling Scheduled'),
        ('REMEDIAL_ASSIGNED', 'Remedial Coursework & Tutoring Assigned'),
        ('PARENT_ADVISED', 'Parent / Guardian Contacted'),
        ('MONITORING', 'Continued Observation & Attendance Tracking'),
        ('NO_ACTION', 'No Immediate Action Required'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='ai_analyses'
    )
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='LOW', db_index=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Composite risk index between 0.00 (Minimal Risk) and 100.00 (Critical Risk)"
    )
    analysis_type = models.CharField(
        max_length=40,
        choices=ANALYSIS_TYPE_CHOICES,
        default='ACADEMIC_EARLY_WARNING'
    )

    # Core academic metrics evaluated
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    missing_assignments_count = models.IntegerField(default=0)
    average_marks_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    leave_days_count = models.IntegerField(default=0)

    # Explainability & Recommendations
    key_risk_drivers = models.JSONField(
        default=list,
        help_text="Natural-language explainable risk factors identified by the model"
    )
    suggested_interventions = models.JSONField(
        default=list,
        help_text="Targeted actionable advisory recommendations for mentors"
    )
    input_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of academic metrics at evaluation time"
    )

    is_latest = models.BooleanField(default=True, db_index=True)
    generated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Human-in-the-loop review workflow
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_ai_analyses'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    review_action_taken = models.CharField(
        max_length=50,
        choices=REVIEW_ACTION_CHOICES,
        blank=True,
        default=''
    )

    class Meta:
        ordering = ['-score', '-generated_at']
        indexes = [
            models.Index(fields=['college', 'risk_level']),
            models.Index(fields=['college', 'student', 'is_latest']),
        ]

    def __str__(self):
        return f"{self.student.roll_number}: {self.risk_level} Risk ({self.score}/100)"
