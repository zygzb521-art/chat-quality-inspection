"""
种子数据脚本：创建初始租户、管理员账号、32条质检规则。
运行方式: python scripts/seed_data.py
"""

import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from apps.tenants.models import Tenant
from apps.rules.models import RuleCategory, Rule

User = get_user_model()

RULES_DATA = [
    # ===== 执行规范 - 响应缺失 =====
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R001', 'name': '响应超时',
        'description': '首条回复超时30分钟且客户交互3次以上未回复',
        'rule_type': 'timing', 'first_penalty': 50, 'second_penalty': 100,
        'third_penalty': 150, 'fourth_penalty': 200,
        'config': {'timeout_minutes': 30, 'min_interactions': 3},
        'hint': '客户等待过久、会话中断',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R002', 'name': '非在岗未回复&微信电话未及时',
        'description': '在岗时间20分钟未回复客户/客户未加微信或未电话跟进',
        'rule_type': 'timing', 'first_penalty': 50, 'second_penalty': 100,
        'third_penalty': 150, 'fourth_penalty': 200,
        'config': {'timeout_minutes': 20},
        'hint': '核对班次、客户属性、微信/电话跟进',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R003', 'name': '在岗10分钟内未提供方案/推荐',
        'description': '客户询价后未及时提供2套以上方案或产品推荐',
        'rule_type': 'timing', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'timeout_minutes': 10},
        'hint': '客户直接要价格时，至少给价格并推荐产品',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R004', 'name': '在岗5分钟内未回复客户顾虑',
        'description': '客户对材质/预算/品质等表示顾虑时未及时有效回应',
        'rule_type': 'timing', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'timeout_minutes': 5},
        'hint': '识别顾虑关键词如"贵""质量""担心"等',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R005', 'name': '无法发图时未告知等待时效',
        'description': '非在岗无法发图时未约定等待时效',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['发不了图', '无法发图', '稍等', '晚点', '回头', '明天发']},
        'hint': '检查是否明确告知等待时效',
    },
    # ===== 执行规范 - 跟进缺失 =====
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R006', 'name': '未填写客户信息&客户询价时未记录客户',
        'description': '客户信息明确但未登记，或询价客户未及时记录',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '需要对接客户信息登记后台',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R007', 'name': '报价后1个工作日内未跟进',
        'description': '已报价或发方案后客户未回复，未在1个工作日内跟进',
        'rule_type': 'timing', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'followup_hours': 24},
        'hint': '约定时间内按约定时间跟',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R008', 'name': '报价后未追',
        'description': '报价后未追回预算、需求匹配、客户未回复原因',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 50,
        'third_penalty': 100, 'fourth_penalty': 150,
        'config': {},
        'hint': '重点看是否挖掘需求、预算匹配、推动决策',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R009', 'name': '发货48小时未回访',
        'description': '客户签收后48小时未做回访（微信/电话）',
        'rule_type': 'timing', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'followup_hours': 48},
        'hint': '需要对接收货确认或物流状态',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R010', 'name': '需要联系方式时未收集',
        'description': '高频定制应在沟通中及时留私域，不应等客户要',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['微信', '电话', '加个', '联系方式', '手机']},
        'hint': '淘宝/1688可直接说，拼多多注意平台规则',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R011', 'name': '询价未下单时未要联系方式',
        'description': '询价未成交客户未留私域丢新客',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '询价未成交重点留联系方式',
    },
    {
        'category_code': 'execution', 'category_name': '执行规范',
        'rule_id': 'R012', 'name': '规格不合适未推荐替代',
        'description': '尺寸/规格/图片等不符合时直接拒绝未推荐替代方案',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['做不了', '没有', '不行', '不可以', '没办法']},
        'hint': '检查是否推荐了UV打印机、转印机等替代',
    },
    # ===== 销售技巧 =====
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R013', 'name': '痛点抓取不足',
        'description': '客户需求明确后客服未针对性推荐',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 50,
        'third_penalty': 100, 'fourth_penalty': 150,
        'config': {},
        'hint': '核对预算、需求、用途、数量、工艺要求',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R014', 'name': '跟进不足',
        'description': '客户质疑/犹豫/价格等，客服回复不匹配未跟进',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '适合作为AI辅助判断项',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R015', 'name': '产品/品牌植入缺失',
        'description': '客户比价/对比时未植入产品优势和品牌亮点',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['对比', '比价', '哪家', '区别']},
        'hint': '提到实机、打印效果、顺滑、团队等',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R016', 'name': '议价环节缺失',
        'description': '首次报价后或客户砍价时未说明优惠空间',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['太贵', '便宜', '优惠', '打折', '少点', '贵了']},
        'hint': '谈价空间、优惠理由、价值说明',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R017', 'name': '压单环节缺失',
        'description': '大额订单未发图/渲染/未提前告知交期/无备用方案',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '关注效果图、色卡选择、打样确认稿',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R018', 'name': '交期环节缺失',
        'description': '过度承诺发货时间，应强调生产时间及顺延风险',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['明天发', '今天发', '马上发', '立刻发']},
        'hint': '不可承诺，只能说正常交期和排单',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R019', 'name': '确认稿未确认',
        'description': '发确认稿/效果图后未要求客户确认',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['确认', '可以', '行', '怎么样', '效果']},
        'hint': '下单前重点确认',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R020', 'name': '推荐连带产品不足',
        'description': '推销主图时未推荐转印/配件/耗材等附加品',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '推荐一个可行方案被拒后尝试另一种',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R021', 'name': '推荐产品与需求不匹配',
        'description': '产品推荐与需求不匹配、预算不符等、推荐方向不对',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 50,
        'third_penalty': 100, 'fourth_penalty': 150,
        'config': {},
        'hint': '参考预算、需求、客户情况',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R022', 'name': '未提供备选方案',
        'description': '预算不匹配时，应推荐其他SKU代替',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '预算超出/不够时推荐替代品追销',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R023', 'name': '预算不足未提供搭配方案',
        'description': '预算不明确时应建议对应SKU并主动引导',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '客户询价但预算不匹配时引导',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R024', 'name': '报价错误',
        'description': '成本计算失误导致价格错误，需后期改价',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 50,
        'third_penalty': 100, 'fourth_penalty': 150,
        'config': {},
        'hint': '产品价格表自动校验',
    },
    {
        'category_code': 'skill', 'category_name': '销售技巧',
        'rule_id': 'R025', 'name': '盈利心态拒单1000元以上',
        'description': '有盈利空间时拒绝客户报价导致丢单',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'min_amount': 1000},
        'hint': '判断毛利和订单价值',
    },
    # ===== 服务态度 =====
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R026', 'name': '未礼貌接待客户',
        'description': '电话强硬、未用敬语、态度生硬',
        'rule_type': 'ai', 'first_penalty': 50, 'second_penalty': 100,
        'third_penalty': 150, 'fourth_penalty': 200,
        'config': {},
        'hint': '态度问题首次重罚',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R027', 'name': '语言不耐烦',
        'description': '已说过、说很多遍、烦不烦等不耐烦用语',
        'rule_type': 'keyword', 'first_penalty': 50, 'second_penalty': 100,
        'third_penalty': 150, 'fourth_penalty': 200,
        'config': {'keywords': ['说过了', '说了很多', '烦不烦', '你听不', '你到底', '有完没完']},
        'hint': '各平台重复接待客户时同理心沟通',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R028', 'name': '冲撞客户',
        'description': '与客户发生言语冲突、对骂',
        'rule_type': 'keyword', 'first_penalty': 50, 'second_penalty': 100,
        'third_penalty': 150, 'fourth_penalty': 200,
        'config': {'keywords': ['傻逼', '滚', '有病', '你什么', '你谁啊']},
        'hint': '态度问题零容忍',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R029', 'name': 'MISS回答',
        'description': '未完整回复客户提问',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '适合作为AI辅助判断项',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R030', 'name': '等级不匹配客服未响应转接',
        'description': '高询单/大客户未转接或交接缺失',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {'keywords': ['大客户', '批量', '大量', '长期', '年单', '出口']},
        'hint': '需配合客户等级体系',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R031', 'name': '丢会话',
        'description': '客户有意向但客服未进一步引导推进至成单',
        'rule_type': 'ai', 'first_penalty': 20, 'second_penalty': 50,
        'third_penalty': 100, 'fourth_penalty': 150,
        'config': {},
        'hint': '结束语后3轮是否还有开单可能',
    },
    {
        'category_code': 'attitude', 'category_name': '服务态度',
        'rule_id': 'R032', 'name': '未主动营销/推荐',
        'description': '客户询价但客服未主动营销或产品推荐',
        'rule_type': 'keyword', 'first_penalty': 20, 'second_penalty': 30,
        'third_penalty': 40, 'fourth_penalty': 50,
        'config': {},
        'hint': '全盘质检优先级最高',
    },
]


def run():
    # Create default tenant
    tenant, created = Tenant.objects.get_or_create(
        slug='default',
        defaults={'name': '默认租户', 'is_active': True},
    )
    if created:
        print(f'创建租户: {tenant.name}')
    else:
        print(f'租户已存在: {tenant.name}')

    # Create super admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': 'super_admin',
            'tenant': tenant,
            'is_staff': True,
            'is_superuser': True,
        },
    )
    if created:
        admin_user.set_password('CHANGE_ME_admin')
        admin_user.save()
        print(f'创建管理员: admin / admin123456')
    else:
        print(f'管理员已存在')

    # Create rule categories and rules
    for rule_data in RULES_DATA:
        cat_code = rule_data.pop('category_code')
        cat_name = rule_data.pop('category_name')

        category, _ = RuleCategory.objects.get_or_create(
            code=cat_code,
            defaults={'name': cat_name},
        )

        rule_id = rule_data['rule_id']
        rule, created = Rule.objects.get_or_create(
            rule_id=rule_id,
            defaults={
                'category': category,
                'name': rule_data['name'],
                'description': rule_data['description'],
                'rule_type': rule_data['rule_type'],
                'first_penalty': rule_data['first_penalty'],
                'second_penalty': rule_data['second_penalty'],
                'third_penalty': rule_data['third_penalty'],
                'fourth_penalty': rule_data['fourth_penalty'],
                'config': rule_data.get('config', {}),
            },
        )
        if created:
            print(f'创建规则: {rule_id} - {rule.name}')

    # Create Celery Beat daily sync schedule (每天凌晨2:00)
    cron, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='2',
        day_of_month='*',
        month_of_year='*',
        day_of_week='*',
        timezone='Asia/Shanghai',
    )
    PeriodicTask.objects.get_or_create(
        name='每日平台采集同步',
        defaults={
            'crontab': cron,
            'task': 'apps.connectors.tasks.daily_platform_sync',
            'enabled': True,
        },
    )

    # Celery Beat: 规则引擎 (每日凌晨3:00, 采集完成后)
    cron3, _ = CrontabSchedule.objects.get_or_create(
        minute='0', hour='3', day_of_month='*',
        month_of_year='*', day_of_week='*', timezone='Asia/Shanghai',
    )
    PeriodicTask.objects.get_or_create(
        name='每日规则引擎质检',
        defaults={
            'crontab': cron3,
            'task': 'apps.rules.tasks.run_rule_engine_for_recent_conversations',
            'enabled': True,
        },
    )

    # Celery Beat: AI分析 (每日凌晨4:00, 质检完成后)
    cron4, _ = CrontabSchedule.objects.get_or_create(
        minute='0', hour='4', day_of_month='*',
        month_of_year='*', day_of_week='*', timezone='Asia/Shanghai',
    )
    PeriodicTask.objects.get_or_create(
        name='每日AI分析',
        defaults={
            'crontab': cron4,
            'task': 'apps.ai_analysis.tasks.batch_ai_analysis',
            'enabled': True,
        },
    )

    # Celery Beat: 日报生成推送 (每日早上8:30)
    cron830, _ = CrontabSchedule.objects.get_or_create(
        minute='30', hour='8', day_of_month='*',
        month_of_year='*', day_of_week='*', timezone='Asia/Shanghai',
    )
    PeriodicTask.objects.get_or_create(
        name='每日日报生成推送',
        defaults={
            'crontab': cron830,
            'task': 'apps.reports.tasks.generate_and_push_daily_report',
            'enabled': True,
        },
    )

    print(f'\n种子数据初始化完成!')
    print(f'  租户: {Tenant.objects.count()}')
    print(f'  规则分类: {RuleCategory.objects.count()}')
    print(f'  规则: {Rule.objects.count()}')
    print(f'  用户: {User.objects.count()}')
    print(f'  定时任务: 采集(2:00) → 质检(3:00) → AI(4:00) → 日报(8:30)')


if __name__ == '__main__':
    run()