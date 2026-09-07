from django.db import models
from apps.tenants.models import Tenant
from apps.conversations.models import PlatformChoices


class ConnectorConfig(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户', related_name='connector_configs')
    platform = models.CharField('平台', max_length=20, choices=PlatformChoices.choices)
    config_data = models.JSONField('凭证配置(加密)', default=dict)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '平台连接配置'
        verbose_name_plural = '平台连接配置'
        unique_together = ('tenant', 'platform')

    def __str__(self):
        return f'[{self.get_platform_display()}] {"启用" if self.is_active else "禁用"}'


class SyncLog(models.Model):
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    platform = models.CharField('平台', max_length=20, choices=PlatformChoices.choices)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField('开始时间', auto_now_add=True)
    finished_at = models.DateTimeField('结束时间', null=True, blank=True)
    conversations_pulled = models.IntegerField('拉取会话数', default=0)
    messages_pulled = models.IntegerField('拉取消息数', default=0)
    error_message = models.TextField('错误信息', blank=True)

    class Meta:
        verbose_name = '同步日志'
        verbose_name_plural = '同步日志'
        ordering = ['-started_at']

    def __str__(self):
        return f'[{self.get_platform_display()}] {self.get_status_display()} @ {self.started_at}'