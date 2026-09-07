from django.contrib import admin
from .models import Tenant, TenantConfig


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')


@admin.register(TenantConfig)
class TenantConfigAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'config_key', 'updated_at')
    list_filter = ('tenant',)