import json
import logging
from decouple import config
import requests

logger = logging.getLogger(__name__)

# Webhook URLs configured via env or TenantConfig
FEISHU_WEBHOOK = config('FEISHU_WEBHOOK', default='')
WEIXIN_WEBHOOK = config('WEIXIN_WEBHOOK', default='')


def push_to_feishu(report) -> bool:
    """Push report to 飞书群机器人 webhook."""
    if not FEISHU_WEBHOOK:
        logger.warning('FEISHU_WEBHOOK not configured, skip push')
        return False

    data = {
        'msg_type': 'interactive',
        'card': {
            'header': {'title': {'tag': 'plain_text', 'content': f'质检日报 {report.report_date}'}},
            'elements': [
                {'tag': 'div', 'text': {'tag': 'lark_md', 'content': (
                    f'**会话总数**: {report.total_conversations}\n'
                    f'**违规数**: {report.violation_count}\n'
                    f'**总扣分**: {report.total_penalty}\n'
                    f'**平均分**: {report.avg_score}\n'
                    f'**高风险会话**: {report.high_risk_count}'
                )}},
                {'tag': 'hr'},
                {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**员工排名**\n' + '\n'.join(
                    f'{i+1}. {e["name"]} 违规{e["count"]}次 扣{e["penalty"]}分'
                    for i, e in enumerate(report.employee_rankings[:5])
                )}},
            ],
        },
    }

    try:
        resp = requests.post(FEISHU_WEBHOOK, json=data, timeout=10)
        resp.raise_for_status()
        logger.info('Feishu push OK: %s', resp.json().get('code'))
        return True
    except Exception as e:
        logger.error('Feishu push failed: %s', e)
        return False


def push_to_weixin(report) -> bool:
    """Push report to 企业微信机器人 webhook."""
    if not WEIXIN_WEBHOOK:
        logger.warning('WEIXIN_WEBHOOK not configured, skip push')
        return False

    content = f'## 质检日报 {report.report_date}\n'
    content += f'> 会话总数: {report.total_conversations}\n'
    content += f'> 违规数: {report.violation_count}\n'
    content += f'> 总扣分: {report.total_penalty}\n'
    content += f'> 平均分: {report.avg_score}\n'
    content += f'> 高风险会话: {report.high_risk_count}\n'

    if report.employee_rankings:
        content += '\n**员工排名**\n'
        for i, e in enumerate(report.employee_rankings[:5]):
            content += f'{i+1}. {e["name"]} 违规{e["count"]}次 扣{e["penalty"]}分\n'

    data = {'msgtype': 'markdown', 'markdown': {'content': content}}

    try:
        resp = requests.post(WEIXIN_WEBHOOK, json=data, timeout=10)
        resp.raise_for_status()
        logger.info('WeChat push OK')
        return True
    except Exception as e:
        logger.error('WeChat push failed: %s', e)
        return False