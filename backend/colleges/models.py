import uuid
from django.db import models
from django.utils.text import slugify
from common.models import TimeStampedModel

class College(TimeStampedModel):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True, help_text="Institutional identifier, e.g. TECH-ENG")
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    domain = models.CharField(max_length=255, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    logo_url = models.URLField(blank=True, max_length=500)
    settings = models.JSONField(default=dict, blank=True, help_text="Configurable college-level preferences")

    class Meta:
        ordering = ['name']
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code or self.name)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'ACTIVE' and not self.is_deleted
