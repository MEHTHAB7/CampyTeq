from django.db import models
from common.models import TenantModel

class Student(TenantModel):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('GRADUATED', 'Graduated'),
        ('SUSPENDED', 'Suspended'),
        ('TRANSFERRED', 'Transferred'),
    ]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='student_profile',
        db_index=True
    )
    student_number = models.CharField(max_length=50, db_index=True, help_text="Unique institutional student ID")
    roll_number = models.CharField(max_length=50, db_index=True, help_text="Class/Batch roll number")
    admission_date = models.DateField()
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='students',
        db_index=True
    )
    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.PROTECT,
        related_name='students',
        db_index=True
    )
    batch = models.ForeignKey(
        'academics.Batch',
        on_delete=models.PROTECT,
        related_name='students',
        db_index=True
    )
    current_semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        db_index=True
    )
    mentor = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_students',
        db_index=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    blood_group = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)

    class Meta:
        ordering = ['roll_number']
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'student_number'],
                condition=models.Q(is_deleted=False),
                name='unique_student_number_per_college'
            ),
            models.UniqueConstraint(
                fields=['batch', 'roll_number'],
                condition=models.Q(is_deleted=False),
                name='unique_roll_number_per_batch'
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number}) - {self.course.code}"


class Guardian(TenantModel):
    RELATIONSHIP_CHOICES = [
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('LEGAL_GUARDIAN', 'Legal Guardian'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guardian_profile'
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    relationship = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES, default='FATHER')
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relationship_display()})"


class StudentGuardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='guardian_relations')
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name='student_relations')
    is_primary = models.BooleanField(default=True)
    emergency_contact = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'guardian')

    def __str__(self):
        return f"{self.student.roll_number} ↔ {self.guardian.first_name}"


class MentorAssignment(TenantModel):
    mentor = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.CASCADE,
        related_name='assigned_cohorts'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='mentor_assignments'
    )
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"Mentor {self.mentor.user.get_full_name()} ➔ Student {self.student.roll_number}"
