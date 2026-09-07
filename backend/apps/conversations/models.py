from django.db import models
from apps.tenants.models import Tenant
from apps.accounts.models import User


class PlatformChoices(models.TextChoices):
    TAOBAO = 'taobao', '淘宝/天猫'
    JD = 'jd', '京东'
    ALI1688 = 'ali1688', '1688'
    PDD = 'pdd', '拼多多'
    YUNKE = 'yunke', '云客CRM'


class Conversation(models.Model):
    STATUS_CHOICES = [
        ('unclosed', '未成交'),
        ('ordered', '已下单'),
        ('paid', '已付款'),
        ('closed', '已关闭'),
    ]
    RISK_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    platform = models.CharField('平台', max_length=20, choices=PlatformChoices.choices)
    conversation_id = models.CharField('会话ID', max_length=200)
    shop_name = models.CharField('店铺名称', max_length=200, blank=True)
    employee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='客服', related_name='conversations'
    )
    customer_name = models.CharField('客户名称', max_length=200, blank=True)
    customer_id = models.CharField('客户ID', max_length=200, blank=True)
    status = models.CharField('会话状态', max_length=20, choices=STATUS_CHOICES, default='unclosed')
    order_amount = models.DecimalField('订单金额', max_digits=12, decimal_places=2, null=True, blank=True)
    has_inquiry = models.BooleanField('是否询价', default=False)
    has_quote = models.BooleanField('是否报价', default=False)
    has_ordered = models.BooleanField('是否下单', default=False)
    has_paid = models.BooleanField('是否付款/锁单', default=False)
    started_at = models.DateTimeField('会话开始时间')
    ended_at = models.DateTimeField('会话结束时间', null=True, blank=True)
    message_count = models.IntegerField('消息数量', default=0)
    total_deduction = models.DecimalField('总扣分', max_digits=6, decimal_places=1, default=0)
    risk_level = models.CharField('风险等级', max_length=10, choices=RISK_CHOICES, default='low')
    ai_suggestion = models.TextField('AI改进建议', blank=True)
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '会话'
        verbose_name_plural = '会话'
        unique_together = ('tenant', 'platform', 'conversation_id')
        indexes = [
            models.Index(fields=['tenant', 'platform', 'started_at']),
            models.Index(fields=['tenant', 'employee']),
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f'[{self.get_platform_display()}] {self.customer_name} ({self.conversation_id})'


class Message(models.Model):
    DIRECTION_CHOICES = [
        ('agent', '客服'),
        ('customer', '客户'),
        ('system', '系统'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages',
        verbose_name='所属会话'
    )
    direction = models.CharField('发送方向', max_length=10, choices=DIRECTION_CHOICES)
    sender_name = models.CharField('发送者', max_length=200, blank=True)
    content = models.TextField('消息内容')
    sent_at = models.DateTimeField('发送时间')
    reply_interval = models.FloatField('回复间隔(分钟)', null=True, blank=True)
    is_ai_generated = models.BooleanField('是否AI生成', default=False)
    msg_sequence = models.IntegerField('消息序号', default=0)
    metadata = models.JSONField('元数据', default=dict, blank=True)

    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['tenant', 'direction']),
        ]
        ordering = ['conversation', 'sent_at']

    def __str__(self):
        return f'[{self.get_direction_display()}] {self.content[:50]}'