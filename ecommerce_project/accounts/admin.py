from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, VendorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Infos supplémentaires", {"fields": ("role", "phone", "address")}),
    )


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "user", "is_approved", "created_at")
    list_filter = ("is_approved",)
