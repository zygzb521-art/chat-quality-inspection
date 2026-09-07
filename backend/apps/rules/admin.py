from django.contrib import admin
from .models import RuleCategory, Rule


@admin.register(RuleCategory)
class RuleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'sort_order')


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('rule_id', 'name', 'category', 'rule_type', 'is_active', 'first_penalty')
    list_filter = ('category', 'rule_type', 'is_active')
    search_fields = ('rule_id', 'name', 'description')