from django.db import models


class Tenant(models.Model):
    name = models.CharField('租户名称', max_length=200)
    slug = models.SlugField('标识', unique=True)
    is_active = models.BooleanField('启用', default=True)
    logo = models.ImageField('Logo', upload_to='tenants/logos/', blank=True)
    primary_color = models.CharField('主题色', max_length=7, default='#409EFF')
    timezone = models.CharField('时区', max_length=50, default='Asia/Shanghai')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '租户'
        verbose_name_plural = '租户'

    def __str__(self):
        return self.name


class TenantConfig(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='configs', verbose_name='租户')
    config_key = models.CharField('配置键', max_length=100)
    config_value = models.JSONField('配置值')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '租户配置'
        verbose_name_plural = '租户配置'
        unique_together = ('tenant', 'config_key')

    def __str__(self):
        return f'{self.tenant.name} - {self.config_key}'
