from django.db import models
from common.models import TenantModel

class Exam(TenantModel):
    EXAM_TYPE_CHOICES = [
        ('INTERNAL', 'Internal Assessment / Sessional'),
        ('SEMESTER', 'Semester Final Examination'),
        ('PRACTICAL', 'Laboratory / Practical Exam'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, db_index=True, help_text="e.g. Mid-Term Examination Fall 2026")
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='INTERNAL')
    batch = models.ForeignKey(
        'academics.Batch',
        on_delete=models.CASCADE,
        related_name='exams',
        db_index=True
    )
    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.CASCADE,
        related_name='exams',
        db_index=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Marks remain hidden from students until published by authorized personnel."
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date', 'name']

    def __str__(self):
        return f"{self.name} ({self.batch.name} - {self.semester.name})"


class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='exam_schedules')
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    maximum_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=40.0)
    room = models.CharField(max_length=100, blank=True, help_text="Allocated Exam Hall")

    class Meta:
        ordering = ['exam_date', 'start_time']
        unique_together = ('exam', 'subject')

    def __str__(self):
        return f"{self.exam.name} - {self.subject.code} ({self.exam_date})"


class Result(TenantModel):
    exam_subject = models.ForeignKey(
        ExamSubject,
        on_delete=models.CASCADE,
        related_name='results',
        db_index=True
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_results',
        db_index=True
    )
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade = models.CharField(max_length=5, blank=True, help_text="e.g. A+, A, B, C, F")
    is_absent = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entered_results'
    )

    class Meta:
        ordering = ['student__roll_number']
        constraints = [
            models.UniqueConstraint(
                fields=['exam_subject', 'student'],
                condition=models.Q(is_deleted=False),
                name='unique_student_exam_subject_result'
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_absent:
            self.grade = 'AB'
        elif not self.grade and self.exam_subject.maximum_marks > 0:
            pct = (float(self.marks_obtained) / float(self.exam_subject.maximum_marks)) * 100
            if pct >= 90:
                self.grade = 'A+'
            elif pct >= 80:
                self.grade = 'A'
            elif pct >= 70:
                self.grade = 'B+'
            elif pct >= 60:
                self.grade = 'B'
            elif pct >= 50:
                self.grade = 'C'
            elif pct >= 40:
                self.grade = 'P'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.roll_number} - {self.exam_subject.subject.code}: {self.marks_obtained}/{self.exam_subject.maximum_marks} ({self.grade})"
