from django.contrib import admin
from .models import Violation, RuleTriggerLog


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'rule', 'employee', 'status', 'penalty_points', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('conversation__customer_name',)


@admin.register(RuleTriggerLog)
class RuleTriggerLogAdmin(admin.ModelAdmin):
    list_display = ('rule', 'conversation', 'employee', 'penalty', 'created_at')
    list_filter = ('rule', 'tenant')