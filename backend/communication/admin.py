from django.contrib import admin
from communication.models import Announcement, Notification, Conversation, Message, Document


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "priority", "target_audience", "published_at", "college"]
    list_filter = ["category", "priority", "target_audience", "college"]
    search_fields = ["title", "content"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "title", "notification_type", "is_read", "created_at", "college"]
    list_filter = ["notification_type", "is_read", "college"]
    search_fields = ["recipient__email", "title", "message"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "last_message_at", "college"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "sender", "content", "is_read", "created_at", "college"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "student", "status", "issued_date", "college"]
    list_filter = ["document_type", "status", "college"]
    search_fields = ["title", "student__roll_number"]
