from django.contrib import admin
 
from products.models import Product, ProductImage
 
 
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['created_at']
 
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'discount_price', 'stock', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'description', 'seller__email']
    ordering = ['-created_at']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    inlines = [ProductImageInline]
 
    actions = ['publish_products', 'archive_products']
 
    @admin.action(description="Tanlangan mahsulotlarni e'lon qilish")
    def publish_products(self, request, queryset):
        queryset.update(status='published')
 
    @admin.action(description="Tanlangan mahsulotlarni arxivlash")
    def archive_products(self, request, queryset):
        queryset.update(status='archived')
 
 
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main', 'created_at']
    list_filter = ['is_main']
    search_fields = ['product__title']
    readonly_fields = ['created_at']
 