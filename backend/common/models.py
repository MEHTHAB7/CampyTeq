import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model providing UUID primary key, timestamps, and soft deletion.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class TenantQuerySet(models.QuerySet):
    """QuerySet for tenant-aware models with active soft-delete filter."""
    def active(self):
        return self.filter(is_deleted=False)

    def for_college(self, college):
        if not college:
            return self.none()
        return self.filter(college=college)


class TenantManager(models.Manager):
    """Manager providing default filtering by soft-deletion and tenant scope."""
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_college(self, college):
        return self.get_queryset().for_college(college)


class TenantModel(TimeStampedModel):
    """
    Abstract base model enforcing multi-tenant isolation.
    Every tenant-owned entity in CampyTeq inherits from this model.
    """
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
        db_index=True
    )

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['college', 'is_deleted']),
        ]
