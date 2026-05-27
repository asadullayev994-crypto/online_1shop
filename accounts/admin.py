from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import ActivityLog, CodeVerify, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "phone_number", "role", "is_verified", "is_banned", "is_active", "created_at"]
    list_filter = ["role", "is_verified", "is_banned", "is_active"]
    search_fields = ["email", "phone_number", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Shaxsiy ma'lumotlar"), {"fields": ("first_name", "last_name", "phone_number", "address", "avatar")}),
        (_("Ruxsatlar"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "is_verified", "is_banned")}),
        (_("Muhim sanalar"), {"fields": ("last_login", "last_seen", "created_at", "updated_at")}),
    )
    readonly_fields = ["last_login", "last_seen", "created_at", "updated_at"]

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone_number", "role", "password1", "password2"),
        }),
    )

    actions = ["ban_users", "unban_users", "verify_users"]

    @admin.action(description="Tanlangan foydalanuvchilarni bloklash")
    def ban_users(self, request, queryset):
        queryset.update(is_banned=True, is_active=False)

    @admin.action(description="Tanlangan foydalanuvchilarni blokdan chiqarish")
    def unban_users(self, request, queryset):
        queryset.update(is_banned=False, is_active=True)

    @admin.action(description="Tanlangan foydalanuvchilarni tasdiqlash")
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)


@admin.register(CodeVerify)
class CodeVerifyAdmin(admin.ModelAdmin):
    list_display = ["user", "code", "purpose", "is_used", "created_at"]
    list_filter = ["purpose", "is_used"]
    search_fields = ["user__email", "code"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "ip_address", "created_at"]
    list_filter = ["action"]
    search_fields = ["user__email", "ip_address"]
    ordering = ["-created_at"]
    readonly_fields = ["user", "action", "ip_address", "created_at"]