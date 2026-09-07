from rest_framework import serializers
from .models import College

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = [
            'id',
            'name',
            'code',
            'slug',
            'domain',
            'email',
            'phone',
            'address',
            'status',
            'logo_url',
            'settings',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CollegeDetailSerializer(CollegeSerializer):
    total_users = serializers.SerializerMethodField()

    class Meta(CollegeSerializer.Meta):
        fields = CollegeSerializer.Meta.fields + ['total_users']

    def get_total_users(self, obj):
        return obj.users.filter(is_deleted=False).count()
