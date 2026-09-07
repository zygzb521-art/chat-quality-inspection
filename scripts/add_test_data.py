"""Create additional test data: employees, training materials, link conversations."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_local'

import django
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.accounts.models import User
from apps.conversations.models import Conversation, Message
from apps.reviews.models import Violation
from apps.training.models import TrainingMaterial
from apps.rules.models import Rule

tenant = Tenant.objects.first()

# Create employee users for the ranking & review workflow
employees_data = [
    ('小王', 'wang', 'cs_agent'),
    ('小李', 'li', 'cs_agent'),
    ('小张', 'zhang', 'cs_agent'),
    ('小赵', 'zhao', 'cs_agent'),
]
employees = []
for name, uname, role in employees_data:
    emp, created = User.objects.get_or_create(
        username=uname,
        defaults={
            'tenant': tenant, 'role': role,
            'email': f'{uname}@example.com',
        },
    )
    if created:
        emp.set_password('123456')
        emp.save()
    employees.append(emp)
    print(f'Employee: {name} ({uname}/{uname}123456)')

# Link conversations to employees
conv_employee_map = {
    'test-taobao': employees[0],   # 小王
    'test-jd': employees[1],       # 小李
    'test-pdd': employees[2],      # 小张
}

for conv in Conversation.objects.all():
    for prefix, emp in conv_employee_map.items():
        if conv.conversation_id.startswith(prefix):
            conv.employee = emp
            conv.save(update_fields=['employee'])
            # Also update violations to link employee
            Violation.objects.filter(conversation=conv).update(employee=emp)
            print(f'Linked {conv.customer_name} -> {emp.username}')
            break

# Create training materials
materials_data = [
    {'title':'客户投诉处理流程','category':'服务态度','priority':'high','content':'1. 先道歉安抚情绪\n2. 了解问题原因\n3. 给出解决方案\n4. 确认客户满意度','rule_id':'R032'},
    {'title':'标准问候话术','category':'执行规范','priority':'medium','content':'客户进线后5秒内响应，首句使用"亲，您好！"\n主动询问需求："请问您想了解什么呢？"','rule_id':'R004'},
    {'title':'价格异议应对技巧','category':'销售技巧','priority':'high','content':'客户说贵时：1. 认同感受 2. 拆分对比 3. 强调价值 4. 推荐替代方案','rule_id':'R016'},
    {'title':'引导下单话术','category':'销售技巧','priority':'medium','content':'当客户表露兴趣时：\n"这款现在有活动，今天下单还赠礼品"\n"我帮您看看库存，稍等~"','rule_id':'R015'},
    {'title':'禁止用语清单','category':'执行规范','priority':'high','content':'严禁使用：\n- "不归我管"\n- "没办法"\n- "规定就是这样"\n- "随便你"','rule_id':'R028'},
]

rules_map = {r.rule_id: r for r in Rule.objects.all()}
for md in materials_data:
    TrainingMaterial.objects.get_or_create(
        title=md['title'],
        tenant=tenant,
        defaults={
            'category': md['category'],
            'priority': md['priority'],
            'content': md['content'],
            'rule': rules_map.get(md['rule_id']),
            'is_published': True,
        },
    )
    print(f'Material: {md["title"]}')

print('\nDone!')
print(f'Employees: {User.objects.filter(tenant=tenant, role="cs_agent").count()}')
print(f'Training materials: {TrainingMaterial.objects.filter(tenant=tenant).count()}')
print(f'Conversations linked: {Conversation.objects.filter(tenant=tenant, employee__isnull=False).count()}')