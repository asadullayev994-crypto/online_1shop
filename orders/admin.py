

from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total_price', 'created_at']

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Umumiy narx"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'id']
    ordering = ['-created_at']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    actions = ['mark_delivering', 'mark_completed', 'mark_cancelled']

    @admin.action(description="Yetkazilmoqda deb belgilash")
    def mark_delivering(self, request, queryset):
        queryset.update(status='delivering')

    @admin.action(description="Yakunlandi deb belgilash")
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    @admin.action(description="Bekor qilindi deb belgilash")
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'created_at']
    search_fields = ['order__id', 'product__title']
    readonly_fields = ['created_at', 'updated_at']