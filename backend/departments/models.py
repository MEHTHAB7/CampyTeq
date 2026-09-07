from django.db import models
from common.models import TenantModel

class Department(TenantModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=50, db_index=True, help_text="e.g. CSE, ECE, MECH")
    hod = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        help_text="Designated Head of Department"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'code'],
                condition=models.Q(is_deleted=False),
                name='unique_department_code_per_college'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
