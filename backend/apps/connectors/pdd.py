import logging
from datetime import datetime
from .base import BaseConnector, ConnectorConversation
from .registry import register_connector

logger = logging.getLogger(__name__)


@register_connector('pdd')
class PDDConnector(BaseConnector):
    """拼多多 聊天记录采集连接器.

    拼多多无官方聊天记录API，使用 Playwright 浏览器自动化采集.
    需部署在有 chromium 的环境 (Dockerfile.celery).

    Config:
        seller_account: 商家账号
        seller_password: 商家密码
        mms_base_url: 拼多多商家后台URL (默认 https://mms.pinduoduo.com)
        headless: 是否无头模式 (默认 True)
    """

    def authenticate(self) -> bool:
        required = ['seller_account', 'seller_password']
        if not all(self.config.get(k) for k in required):
            logger.error('PDD auth failed: missing account credentials')
            return False
        return True

    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        # TODO: Playwright → 登录MMS → 进入聊天记录页面 → 抓取会话列表
        logger.info('PDD pull_conversations: %s ~ %s', start_time, end_time)
        return []

    def pull_messages(self, conversation_id: str) -> list[dict]:
        # TODO: Playwright → 点击会话 → 滚动加载全部消息 → 提取消息
        logger.info('PDD pull_messages: %s', conversation_id)
        return []

    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        return ConnectorConversation(
            platform='pdd',
            conversation_id=raw.get('conversation_id', ''),
            shop_name=raw.get('shop_name', ''),
            customer_name=raw.get('customer_name', ''),
            customer_id=raw.get('customer_id', ''),
            employee_name=raw.get('service_staff_name', ''),
            status=raw.get('status', 'unclosed'),
            started_at=raw.get('started_at'),
            ended_at=raw.get('ended_at'),
            raw_data=raw,
        )