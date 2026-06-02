

from django.contrib import admin

from cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'created_at']

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Umumiy narx"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = "Mahsulot soni"

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = "Umumiy narx"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'created_at']
    search_fields = ['cart__user__email', 'product__title']
    readonly_fields = ['created_at', 'updated_at']