from django.contrib import admin
from .models import TrainingMaterial


@admin.register(TrainingMaterial)
class TrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'rule', 'is_published', 'created_at')
    list_filter = ('category', 'priority', 'is_published', 'tenant')
    search_fields = ('title', 'content')