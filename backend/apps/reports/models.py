from django.db import models
from apps.tenants.models import Tenant


class Report(models.Model):
    STATUS_CHOICES = [
        ('draft', '待推送'),
        ('sent', '已推送'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', related_name='reports')
    report_date = models.DateField('日报日期')
    total_conversations = models.IntegerField('会话总数', default=0)
    violation_count = models.IntegerField('违规数', default=0)
    total_penalty = models.IntegerField('总扣分', default=0)
    high_risk_count = models.IntegerField('高风险会话数', default=0)
    avg_score = models.FloatField('平均分', default=100.0)
    employee_rankings = models.JSONField('员工排名', default=list)
    rule_distribution = models.JSONField('规则分布', default=list)
    high_risk_sessions = models.JSONField('高风险会话', default=list)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '日报'
        verbose_name_plural = '日报'
        unique_together = ('tenant', 'report_date')
        ordering = ['-report_date']

    def __str__(self):
        return f'日报 {self.report_date} [{self.get_status_display()}]'