from django.db import models
from common.models import TenantModel

class Faculty(TenantModel):
    DESIGNATION_CHOICES = [
        ('PROFESSOR', 'Professor'),
        ('ASSOCIATE_PROFESSOR', 'Associate Professor'),
        ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
        ('LECTURER', 'Lecturer'),
        ('LAB_INSTRUCTOR', 'Lab Instructor'),
    ]

    EMPLOYMENT_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('VISITING', 'Visiting'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('RESIGNED', 'Resigned'),
        ('RETIRED', 'Retired'),
    ]

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        db_index=True
    )
    faculty_number = models.CharField(max_length=50, db_index=True, help_text="Unique institutional employee code")
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT,
        related_name='faculty_members',
        db_index=True
    )
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES, default='ASSISTANT_PROFESSOR')
    qualification = models.CharField(max_length=200, help_text="e.g. Ph.D. in Computer Science, M.Tech")
    specialization = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField()
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_CHOICES, default='FULL_TIME')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    emergency_contact = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['faculty_number']
        verbose_name = 'Faculty Member'
        verbose_name_plural = 'Faculty Members'
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'faculty_number'],
                condition=models.Q(is_deleted=False),
                name='unique_faculty_number_per_college'
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.faculty_number}) - {self.get_designation_display()}"
