from rest_framework import serializers
from .models import CameraZone, Camera


class CameraZoneSerializer(serializers.ModelSerializer):
    camera_count = serializers.SerializerMethodField()
    online_camera_count = serializers.SerializerMethodField()

    class Meta:
        model = CameraZone
        fields = [
            'id', 'name', 'code', 'building', 'floor',
            'description', 'is_active', 'camera_count',
            'online_camera_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_camera_count(self, obj):
        return obj.cameras.filter(is_active=True).count()

    def get_online_camera_count(self, obj):
        return obj.cameras.filter(is_active=True, status='ONLINE').count()


class CameraSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    zone_code = serializers.CharField(source='zone.code', read_only=True)
    building = serializers.CharField(source='zone.building', read_only=True)
    floor = serializers.IntegerField(source='zone.floor', read_only=True)

    class Meta:
        model = Camera
        fields = [
            'id', 'zone', 'zone_name', 'zone_code', 'building', 'floor',
            'name', 'code', 'camera_type', 'ip_address', 'rtsp_url',
            'location_description', 'status', 'last_heartbeat',
            'resolution', 'fps', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CameraHeartbeatSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Camera.STATUS_CHOICES, default='ONLINE')
    fps = serializers.IntegerField(required=False, min_value=1, max_value=120)
