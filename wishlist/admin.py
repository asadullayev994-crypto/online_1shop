
from django.contrib import admin

from wishlist.models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_count', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WishlistItemInline]

    def total_count(self, obj):
        return obj.items.count()
    total_count.short_description = "Mahsulotlar soni"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'product', 'created_at']
    search_fields = ['wishlist__user__email', 'product__title']
    readonly_fields = ['created_at', 'updated_at']