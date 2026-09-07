from django.db import models


class RuleCategory(models.Model):
    name = models.CharField('分类名称', max_length=100)
    code = models.CharField('分类编码', max_length=20, unique=True)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '规则分类'
        verbose_name_plural = '规则分类'

    def __str__(self):
        return self.name


class Rule(models.Model):
    RULE_TYPES = [
        ('keyword', '关键词匹配'),
        ('timing', '时间检测'),
        ('ai', 'AI判断'),
        ('hybrid', '混合检测'),
    ]
    category = models.ForeignKey(RuleCategory, on_delete=models.CASCADE, verbose_name='规则分类', related_name='rules')
    rule_id = models.CharField('规则ID', max_length=10, unique=True)
    name = models.CharField('规则名称', max_length=200)
    description = models.TextField('规则描述', blank=True)
    rule_type = models.CharField('规则类型', max_length=20, choices=RULE_TYPES, default='keyword')
    config = models.JSONField('规则参数', default=dict, blank=True)
    first_penalty = models.IntegerField('首次扣分', default=20)
    second_penalty = models.IntegerField('二次扣分', default=30)
    third_penalty = models.IntegerField('三次扣分', default=40)
    fourth_penalty = models.IntegerField('四次扣分', default=50)
    is_active = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '质检规则'
        verbose_name_plural = '质检规则'

    def __str__(self):
        return f'{self.rule_id} {self.name}'

    def get_penalty(self, offense_count: int) -> int:
        if offense_count >= 4:
            return self.fourth_penalty
        elif offense_count >= 3:
            return self.third_penalty
        elif offense_count >= 2:
            return self.second_penalty
        else:
            return self.first_penalty