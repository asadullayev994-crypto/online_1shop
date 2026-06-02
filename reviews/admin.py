

from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['user__email', 'product__title', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description="Tanlangan sharhlarni tasdiqlash")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Tanlangan sharhlarni rad etish")
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)