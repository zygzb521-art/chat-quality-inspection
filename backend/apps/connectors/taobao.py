import logging
from datetime import datetime
from .base import BaseConnector, ConnectorConversation, ConnectorMessage
from .registry import register_connector

logger = logging.getLogger(__name__)


@register_connector('taobao')
class TaobaoConnector(BaseConnector):
    """淘宝/天猫 千牛瓦力服务 API 连接器.

    Config:
        app_key: 千牛应用AppKey
        app_secret: 千牛应用AppSecret
        refresh_token: 卖家授权refresh_token
        seller_nick: 卖家昵称
        session_key: 卖家session key (可选, 优先使用)
    """

    API_BASE = 'https://gw.api.taobao.com/router/rest'

    def authenticate(self) -> bool:
        self._auth_result = {
            'app_key': self.config.get('app_key'),
            'app_secret': self.config.get('app_secret'),
            'session_key': self.config.get('session_key') or self.config.get('refresh_token'),
        }
        required = ['app_key', 'app_secret']
        if not all(self._auth_result.get(k) for k in required):
            logger.error('Taobao auth failed: missing app_key or app_secret')
            return False
        return True

    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        # TODO: call taobao.qianniu.conversation.get or similar API
        logger.info('Taobao pull_conversations: %s ~ %s', start_time, end_time)
        return []

    def pull_messages(self, conversation_id: str) -> list[dict]:
        # TODO: call taobao.qianniu.message.list or similar API
        logger.info('Taobao pull_messages: %s', conversation_id)
        return []

    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        return ConnectorConversation(
            platform='taobao',
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