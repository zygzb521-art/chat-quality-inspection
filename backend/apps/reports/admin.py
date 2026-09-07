from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'tenant', 'total_conversations', 'violation_count', 'avg_score', 'status', 'created_at')
    list_filter = ('status', 'tenant')
    date_hierarchy = 'report_date'