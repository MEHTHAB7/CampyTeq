from django.db import models
from common.models import TenantModel

class Assignment(TenantModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Accepting Submissions'),
        ('CLOSED', 'Closed / Submissions Locked'),
    ]

    faculty = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.CASCADE,
        related_name='assignments',
        db_index=True
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
        db_index=True
    )
    batch = models.ForeignKey(
        'academics.Batch',
        on_delete=models.CASCADE,
        related_name='assignments',
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    attachment_url = models.URLField(blank=True, max_length=500)
    maximum_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    due_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.subject.code}: {self.title} (Due {self.due_date.strftime('%Y-%m-%d')})"


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Submission'),
        ('SUBMITTED', 'Submitted on Time'),
        ('LATE', 'Submitted Late'),
        ('GRADED', 'Graded & Feedback Provided'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        db_index=True
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        db_index=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    file_url = models.URLField(blank=True, max_length=500)
    submission_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED', db_index=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_assignments'
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.roll_number} ➔ {self.assignment.title} ({self.status})"
