from django.db import models
from apps.tenants.models import Tenant
from apps.rules.models import Rule


class TrainingMaterial(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    rule = models.ForeignKey(Rule, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联规则')
    category = models.CharField('分类', max_length=50, blank=True, help_text='eg. 服务态度, 销售技巧')
    priority = models.CharField('优先级', max_length=10, choices=[
        ('high', '高'), ('medium', '中'), ('low', '低'),
    ], default='medium')
    is_published = models.BooleanField('发布', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '培训素材'
        verbose_name_plural = '培训素材'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title