from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.tenants.models import Tenant


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('inspector', '质检员'),
        ('cs_manager', '客服主管'),
        ('cs_agent', '客服'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, verbose_name='租户')
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='cs_agent')
    employee_id = models.CharField('工号', max_length=50, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    platform_accounts = models.JSONField('平台账号映射', default=dict, blank=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'