from rest_framework import serializers

from notifications.models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "notification_type",
            "notification_type_display", "is_read", "read_at", "created_at",
        ]
        read_only_fields = [
            "id", "title", "message", "notification_type",
            "notification_type_display", "is_read", "read_at", "created_at",
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "order_updates", "payment_updates",
            "promotions", "system_updates",
        ]