

from django.contrib import admin

from notifications.models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__email', 'title', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'read_at']

    actions = ['mark_as_read']

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_read=True, read_at=timezone.now())


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_updates', 'payment_updates', 'promotions', 'system_updates']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']