from django.contrib import admin
 
from categories.models import Category
 
 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'slug']
    ordering = ['name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
 