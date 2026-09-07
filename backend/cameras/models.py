from django.db import models
from common.models import TenantModel


class CameraZone(TenantModel):
    """Physical zone or sector on campus monitored by stationary cameras."""
    name = models.CharField(max_length=150, help_text="e.g. Main Gate 1, CSE Lab 2")
    code = models.CharField(max_length=50, db_index=True, help_text="e.g. ZONE-GATE-1")
    building = models.CharField(max_length=150, help_text="e.g. Academic Block A, Gatehouse")
    floor = models.IntegerField(default=0, help_text="0 for Ground floor, 1 for 1st floor, etc.")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['building', 'floor', 'name']
        unique_together = ('college', 'code')

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.building}"


class Camera(TenantModel):
    """Stationary authorized IP/RTSP camera registered in a specific zone."""
    CAMERA_TYPE_CHOICES = [
        ('DOME', 'Dome Camera'),
        ('BULLET', 'Bullet Camera'),
        ('PTZ', 'Pan-Tilt-Zoom (PTZ)'),
        ('FISHEYE', '360° Fisheye'),
    ]

    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    zone = models.ForeignKey(CameraZone, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=150, help_text="e.g. Gate 1 North Walkway")
    code = models.CharField(max_length=50, db_index=True, help_text="e.g. CAM-GATE-01")
    camera_type = models.CharField(max_length=30, choices=CAMERA_TYPE_CHOICES, default='DOME')
    ip_address = models.CharField(max_length=50, blank=True)
    rtsp_url = models.CharField(max_length=500, blank=True)
    location_description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONLINE', db_index=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    resolution = models.CharField(max_length=20, default='1080p')
    fps = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        unique_together = ('college', 'code')

    def __str__(self):
        return f"{self.code}: {self.name} [{self.zone.code}] ({self.status})"
