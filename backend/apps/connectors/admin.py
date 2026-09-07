from django.contrib import admin
from .models import ConnectorConfig, SyncLog


@admin.register(ConnectorConfig)
class ConnectorConfigAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'platform', 'is_active', 'created_at', 'updated_at')
    list_filter = ('platform', 'is_active', 'tenant')
    search_fields = ('tenant__name',)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'platform', 'status', 'conversations_pulled', 'messages_pulled', 'started_at', 'finished_at')
    list_filter = ('platform', 'status', 'tenant')
    readonly_fields = ('started_at', 'finished_at')