"""Create test conversations and run rule engine for local demo."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_local'

import django
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.conversations.models import Conversation, Message
from apps.rules.engine import RuleEngine
from apps.reviews.models import Violation

tenant = Tenant.objects.first()
now = timezone.now()

convs_data = [
    {
        'platform': 'taobao',
        'customer': '张三',
        'employee_name': '客服小王',
        'shop': '旗舰店',
        'messages': [
            ('customer', '在吗？'),
            ('agent', '不行，没办法，规定就是这样'),
            ('customer', '能不能便宜点'),
            ('agent', '不行，不能便宜'),
            ('customer', '那我不买了'),
            ('agent', '随便你'),
        ]
    },
    {
        'platform': 'jd',
        'customer': '李四',
        'employee_name': '客服小李',
        'shop': '数码专营店',
        'messages': [
            ('customer', '你好，这个手机多少钱？'),
            ('agent', '亲，您好！这款手机今天有优惠活动，满减后只要2999'),
            ('customer', '比别家贵啊'),
            ('agent', '您可以对比一下配置，我们这款性价比很高的'),
            ('customer', '好吧，下单了'),
            ('agent', '感谢您的信任！下单后可以参加抽奖活动'),
        ]
    },
    {
        'platform': 'pdd',
        'customer': '王五',
        'employee_name': '客服小张',
        'shop': '家居生活馆',
        'messages': [
            ('customer', '这个桌子有质量问题！'),
            ('agent', '不好意思，让您遇到这个问题了'),
            ('customer', '我要退货退款'),
            ('agent', '不归我管，你去找售后'),
            ('customer', '你什么态度？'),
            ('agent', '没办法，这不是我的问题'),
        ]
    },
]

for cd in convs_data:
    conv = Conversation.objects.create(
        tenant=tenant,
        platform=cd['platform'],
        conversation_id=f'test-{cd["platform"]}-{now.timestamp():.0f}',
        customer_name=cd['customer'],
        shop_name=cd['shop'],
        started_at=now - timezone.timedelta(hours=2),
        has_inquiry=True,
    )
    for i, (direction, content) in enumerate(cd['messages']):
        Message.objects.create(
            tenant=tenant,
            conversation=conv,
            direction=direction,
            content=content,
            sender_name=cd['employee_name'] if direction == 'agent' else cd['customer'],
            sent_at=now - timezone.timedelta(hours=2) + timezone.timedelta(minutes=i * 5),
        )
    print(f'Created conversation: {cd["platform"]} - {cd["customer"]} ({conv.id})')

# Run rule engine on all conversations
print('\nRunning rule engine...')
for conv in Conversation.objects.all():
    engine = RuleEngine(conv)
    total = engine.apply()
    matched_violations = Violation.objects.filter(conversation=conv).select_related('rule')
    for v in matched_violations:
        print(f'  VIOLATION: conv={conv.id} ({conv.platform}) rule={v.rule.rule_id} penalty={v.penalty_points}')

violation_count = Violation.objects.count()
print(f'\nTotal violations created: {violation_count}')

for conv in Conversation.objects.all():
    v = Violation.objects.filter(conversation=conv).select_related('rule')
    violations_list = [(vv.rule.rule_id, vv.penalty_points) for vv in v]
    print(f'  Conv {conv.id} ({conv.platform}/{conv.customer_name}): total_deduction={conv.total_deduction}, risk={conv.risk_level}, violations={violations_list}')