from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'tenant', 'employee_id', 'is_active')
    list_filter = ('role', 'tenant', 'is_active')
    search_fields = ('username', 'email', 'employee_id')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('tenant', 'role', 'employee_id', 'phone', 'platform_accounts')}),
    )