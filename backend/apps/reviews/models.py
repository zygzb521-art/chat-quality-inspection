from django.db import models
from apps.tenants.models import Tenant
from apps.accounts.models import User
from apps.conversations.models import Conversation
from apps.rules.models import Rule


class RuleTriggerLog(models.Model):
    """规则命中日志 — 每次规则被触发记录一条."""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name='会话', related_name='rule_triggers')
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, verbose_name='规则')
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='客服')
    matched_content = models.TextField('命中内容', blank=True)
    matched_keyword = models.CharField('命中关键词', max_length=200, blank=True)
    evidence = models.JSONField('证据', default=dict, blank=True)
    penalty = models.IntegerField('本次扣分', default=0)
    created_at = models.DateTimeField('触发时间', auto_now_add=True)

    class Meta:
        verbose_name = '规则命中日志'
        verbose_name_plural = '规则命中日志'
        indexes = [
            models.Index(fields=['conversation', 'rule']),
            models.Index(fields=['tenant', 'employee']),
        ]

    def __str__(self):
        return f'{self.rule.rule_id} → {self.conversation} (-{self.penalty})'


class Violation(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('appealed', '已申述'),
        ('confirmed', '已确认'),
        ('closed', '已关闭'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name='会话', related_name='violations')
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, verbose_name='规则')
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='客服')
    rule_trigger = models.ForeignKey(RuleTriggerLog, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联命中日志')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    penalty_points = models.IntegerField('扣分', default=0)
    adjusted_penalty = models.IntegerField('调整后扣分', null=True, blank=True)
    evidence_text = models.TextField('违规证据', blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='复核人', related_name='reviewed_violations')
    review_notes = models.TextField('复核备注', blank=True)
    reviewed_at = models.DateTimeField('复核时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '违规单'
        verbose_name_plural = '违规单'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'employee', 'status']),
            models.Index(fields=['conversation', 'rule']),
        ]

    def __str__(self):
        return f'{self.rule.rule_id} - {self.conversation} [{self.get_status_display()}]'