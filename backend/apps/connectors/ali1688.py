import logging
from datetime import datetime
from .base import BaseConnector, ConnectorConversation
from .registry import register_connector

logger = logging.getLogger(__name__)


@register_connector('ali1688')
class Ali1688Connector(BaseConnector):
    """1688 开放平台 API 连接器.

    Config:
        app_key: 1688应用AppKey
        app_secret: 1688应用AppSecret
        access_token: 商家授权access_token
    """

    API_BASE = 'https://gw.open.1688.com/openapi/'

    def authenticate(self) -> bool:
        required = ['app_key', 'app_secret', 'access_token']
        if not all(self.config.get(k) for k in required):
            logger.error('Ali1688 auth failed: missing required credentials')
            return False
        self._auth_result = {k: self.config[k] for k in required}
        return True

    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        # TODO: call alibaba.1688.im.conversation.list or similar API
        logger.info('Ali1688 pull_conversations: %s ~ %s', start_time, end_time)
        return []

    def pull_messages(self, conversation_id: str) -> list[dict]:
        # TODO: call alibaba.1688.im.message.list or similar API
        logger.info('Ali1688 pull_messages: %s', conversation_id)
        return []

    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        return ConnectorConversation(
            platform='ali1688',
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