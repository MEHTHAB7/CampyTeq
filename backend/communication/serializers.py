from rest_framework import serializers
from communication.models import Announcement, Notification, Conversation, Message, Document
from accounts.models import User


class AnnouncementSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "category",
            "priority",
            "target_audience",
            "department",
            "department_name",
            "created_by",
            "created_by_name",
            "is_pinned",
            "published_at",
            "expires_at",
            "attachment_url",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "action_url",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["recipient", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
            "sender_role",
            "content",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["sender", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    participant_details = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "subject",
            "participants",
            "participant_details",
            "last_message",
            "last_message_at",
        ]

    def get_participant_details(self, obj):
        return [
            {
                "id": str(u.id),
                "name": u.get_full_name(),
                "role": u.role,
                "email": u.email,
            }
            for u in obj.participants.all()
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None


class DocumentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_roll = serializers.CharField(source="student.roll_number", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "document_type",
            "student",
            "student_name",
            "student_roll",
            "uploaded_by",
            "uploaded_by_name",
            "file_url",
            "status",
            "issued_date",
            "created_at",
        ]
        read_only_fields = ["uploaded_by", "created_at"]
