from django.db import models
from apps.tenants.models import Tenant
from apps.conversations.models import Conversation


class AIAnalysisResult(models.Model):
    STATUS_CHOICES = [
        ('pending', '待分析'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name='会话', related_name='ai_results')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    attitude_score = models.IntegerField('态度评分', null=True, blank=True)
    attitude_detail = models.JSONField('态度分析详情', default=dict, blank=True)
    skill_score = models.IntegerField('销售技巧评分', null=True, blank=True)
    skill_detail = models.JSONField('销售技巧分析详情', default=dict, blank=True)
    suggestions = models.JSONField('改进建议', default=list, blank=True)
    ai_suggestion_text = models.TextField('AI建议文本', blank=True)
    raw_response = models.JSONField('原始响应', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'AI分析结果'
        verbose_name_plural = 'AI分析结果'
        indexes = [
            models.Index(fields=['conversation', 'status']),
        ]

    def __str__(self):
        return f'AI分析 {self.conversation} [{self.get_status_display()}]'