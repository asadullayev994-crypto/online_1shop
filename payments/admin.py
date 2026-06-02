
from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order', 'method', 'status', 'amount', 'currency', 'paid_at', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['user__email', 'transaction_id', 'order__id']
    ordering = ['-created_at']
    readonly_fields = ['transaction_id', 'paid_at', 'created_at', 'updated_at']

    actions = ['mark_as_paid', 'mark_as_refunded']

    @admin.action(description="To'landi deb belgilash")
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='paid', paid_at=timezone.now())

    @admin.action(description="Qaytarildi deb belgilash")
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')