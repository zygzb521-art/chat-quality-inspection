"""Seed database for local SQLite dev."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_local'

import django
django.setup()

from django.utils import timezone
from apps.tenants.models import Tenant
from apps.rules.models import RuleCategory, Rule
from apps.accounts.models import User

if Tenant.objects.exists():
    print('Data already seeded, skipping.')
    sys.exit(0)

tenant = Tenant.objects.create(name='默认租户', slug='default')
print(f'Tenant created: id={tenant.id}')

admin = User.objects.create_superuser(
    username='admin', email='admin@example.com',
    password='CHANGE_ME_admin', tenant=tenant,
    role='super_admin', phone='13800138000',
)
print(f'Admin created: admin/CHANGE_ME_admin  ⚠️  首次登录后请立即修改')
inspector = User.objects.create_user(
    username='inspector', password='CHANGE_ME_inspector',
    tenant=tenant, role='inspector',
)
print(f'Inspector created: inspector/CHANGE_ME_inspector')

categories_data = {
    'execution': ('执行规范', 1),
    'sales_skill': ('销售技巧', 2),
    'service_attitude': ('服务态度', 3),
}
for code, (name, order) in categories_data.items():
    RuleCategory.objects.create(code=code, name=name, sort_order=order)

RULES_DATA = [
    {'category':'execution','id':'R001','name':'响应超时','type':'timing','p1':50,'p2':100,'p3':150,'p4':200,'hint':'客户等待过久','config':{'timeout_minutes':30,'min_interactions':3}},
    {'category':'execution','id':'R002','name':'回复间隔过长','type':'timing','p1':30,'p2':60,'p3':90,'p4':120,'hint':'回复间隔超过20分钟','config':{'timeout_minutes':20,'min_interactions':5}},
    {'category':'execution','id':'R003','name':'缺少结束语','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'缺少感谢/再见等结束语','config':{'keywords':['再见','欢迎下次','感谢','祝您']}},
    {'category':'execution','id':'R004','name':'缺少开头问候语','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'首条消息缺少问候','config':{'keywords':['您好','你好','欢迎','亲']}},
    {'category':'execution','id':'R005','name':'未关闭重复会话','type':'keyword','p1':30,'p2':60,'p3':90,'p4':120,'hint':'存在多个相同客户的未关闭会话','config':{'keywords':[]}},
    {'category':'execution','id':'R006','name':'不当承诺','type':'keyword','p1':50,'p2':100,'p3':150,'p4':200,'hint':'承诺退款/赠品等','config':{'keywords':['保证','承诺','绝对没问题']}},
    {'category':'execution','id':'R007','name':'首响时间过长','type':'timing','p1':30,'p2':60,'p3':90,'p4':120,'hint':'首次响应超过3分钟','config':{'timeout_minutes':3}},
    {'category':'execution','id':'R008','name':'服务态度生硬','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'未使用礼貌用语','config':{'keywords':['没办法','不行','不可以','不能','规定就是这样']}},
    {'category':'execution','id':'R009','name':'索要好评','type':'keyword','p1':30,'p2':60,'p3':90,'p4':120,'hint':'索要好评违反平台规则','config':{'keywords':['给好评','五星好评','好评返现','追加评价']}},
    {'category':'execution','id':'R010','name':'引导线下交易','type':'keyword','p1':100,'p2':200,'p3':300,'p4':500,'hint':'严重违规','config':{'keywords':['加微信','加QQ','私下交易','银行转账','支付宝转账']}},
    {'category':'execution','id':'R011','name':'泄露客户隐私','type':'keyword','p1':100,'p2':200,'p3':300,'p4':500,'hint':'泄露手机号/地址等','config':{'keywords':[]}},
    {'category':'execution','id':'R012','name':'未按流程操作','type':'keyword','p1':30,'p2':60,'p3':90,'p4':120,'hint':'退货/换货/退款流程不合规','config':{'keywords':[]}},
    {'category':'sales_skill','id':'R013','name':'未挖掘需求','type':'ai','p1':20,'p2':40,'p3':60,'p4':80,'hint':'未主动了解客户需求','config':{'prompt_hint':'判断客服是否主动询问客户需求'}},
    {'category':'sales_skill','id':'R014','name':'未主动推荐','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'未在客户犹豫时推荐','config':{'keywords':['推荐','建议您','可以试试','这款适合']}},
    {'category':'sales_skill','id':'R015','name':'未引导下单','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'未在客户有意向时引导下单','config':{'keywords':['下单','去拍','加购','结算']}},
    {'category':'sales_skill','id':'R016','name':'未处理价格异议','type':'keyword','p1':30,'p2':60,'p3':90,'p4':120,'hint':'客户嫌贵时未有效应对','config':{'keywords':['贵','太贵了','价格高','不值']}},
    {'category':'sales_skill','id':'R017','name':'未处理对比异议','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'客户对比竞品时未有效应对','config':{'keywords':['比别家','别人家','不如','对比']}},
    {'category':'sales_skill','id':'R018','name':'未使用促销话术','type':'keyword','p1':10,'p2':20,'p3':30,'p4':40,'hint':'未主动告知优惠/活动','config':{'keywords':['优惠','打折','满减','赠品','限时']}},
    {'category':'sales_skill','id':'R019','name':'未追加销售','type':'keyword','p1':15,'p2':30,'p3':45,'p4':60,'hint':'未在客户下单后推荐搭配商品','config':{'keywords':['搭配','加','划算','套餐']}},
    {'category':'sales_skill','id':'R020','name':'未做客户安抚','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'投诉时未先安抚情绪','config':{'keywords':['抱歉','理解','消消气','不要着急']}},
    {'category':'sales_skill','id':'R021','name':'未确认需求细节','type':'keyword','p1':15,'p2':30,'p3':45,'p4':60,'hint':'未确认规格/数量/颜色等','config':{'keywords':['规格','尺寸','颜色','数量']}},
    {'category':'sales_skill','id':'R022','name':'未提供增值方案','type':'ai','p1':20,'p2':40,'p3':60,'p4':80,'hint':'未提供高性价比推荐','config':{'prompt_hint':'判断客服是否主动提供增值方案'}},
    {'category':'sales_skill','id':'R023','name':'未促进成交','type':'ai','p1':25,'p2':50,'p3':75,'p4':100,'hint':'未把握成交时机','config':{'prompt_hint':'判断客服是否主动促进成交'}},
    {'category':'sales_skill','id':'R024','name':'未引导复购','type':'keyword','p1':15,'p2':30,'p3':45,'p4':60,'hint':'未在售后引导再次购买','config':{'keywords':['下次','新款','上新','关注']}},
    {'category':'service_attitude','id':'R025','name':'语气生硬','type':'ai','p1':30,'p2':60,'p3':90,'p4':120,'hint':'语气冷漠/生硬','config':{'prompt_hint':'判断客服语气是否生硬不友好'}},
    {'category':'service_attitude','id':'R026','name':'缺乏同理心','type':'ai','p1':30,'p2':60,'p3':90,'p4':120,'hint':'未站在客户角度理解问题','config':{'prompt_hint':'判断客服是否缺乏同理心'}},
    {'category':'service_attitude','id':'R027','name':'情绪冲突','type':'ai','p1':50,'p2':100,'p3':150,'p4':200,'hint':'与客户发生争吵/冲突','config':{'prompt_hint':'判断是否与客户发生情绪冲突'}},
    {'category':'service_attitude','id':'R028','name':'频繁使用否定语气','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'连续使用不行/不可以等','config':{'keywords':['不行','不可以','不能','不可能','没办法']}},
    {'category':'service_attitude','id':'R029','name':'推卸责任','type':'keyword','p1':30,'p2':60,'p3':90,'p4':120,'hint':'将责任推给客户/其他部门','config':{'keywords':['不归我管','不是我的问题','你去找','跟我没关系']}},
    {'category':'service_attitude','id':'R030','name':'不积极响应','type':'ai','p1':20,'p2':40,'p3':60,'p4':80,'hint':'敷衍回复/答非所问','config':{'prompt_hint':'判断客服是否敷衍或不积极响应'}},
    {'category':'service_attitude','id':'R031','name':'未使用礼貌称呼','type':'keyword','p1':10,'p2':20,'p3':30,'p4':40,'hint':'未使用亲/您等称呼','config':{'keywords':['亲','您好','您']}},
    {'category':'service_attitude','id':'R032','name':'未道歉','type':'keyword','p1':20,'p2':40,'p3':60,'p4':80,'hint':'客户不满时未先道歉','config':{'keywords':['抱歉','对不起','不好意思','道歉','向您道歉']}},
]

cats = {c.code: c for c in RuleCategory.objects.all()}
for d in RULES_DATA:
    Rule.objects.create(
        rule_id=d['id'], category=cats[d['category']],
        name=d['name'], description=d.get('hint',''),
        rule_type=d['type'], config=d['config'],
        first_penalty=d['p1'], second_penalty=d['p2'],
        third_penalty=d['p3'], fourth_penalty=d['p4'],
        sort_order=int(d['id'][1:]), is_active=True,
    )
print(f'Created {Rule.objects.count()} rules')

print('Seed complete.')
print(f'Admin: admin/admin123456')
print(f'Inspector: inspector/inspector123')