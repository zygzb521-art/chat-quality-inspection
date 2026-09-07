import logging
from datetime import datetime
from .base import BaseConnector, ConnectorConversation
from .registry import register_connector

logger = logging.getLogger(__name__)


@register_connector('jd')
class JDConnector(BaseConnector):
    """京东 JOS 开放平台 API 连接器.

    Config:
        app_key: JOS应用AppKey
        app_secret: JOS应用AppSecret
        access_token: 商家授权access_token
        shop_id: 店铺ID
    """

    API_BASE = 'https://api.jd.com/routerjson'

    def authenticate(self) -> bool:
        required = ['app_key', 'app_secret', 'access_token']
        if not all(self.config.get(k) for k in required):
            logger.error('JD auth failed: missing required credentials')
            return False
        self._auth_result = {k: self.config[k] for k in required}
        return True

    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        # TODO: call jd.im.conversation.list or similar API
        logger.info('JD pull_conversations: %s ~ %s', start_time, end_time)
        return []

    def pull_messages(self, conversation_id: str) -> list[dict]:
        # TODO: call jd.im.message.list or similar API
        logger.info('JD pull_messages: %s', conversation_id)
        return []

    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        return ConnectorConversation(
            platform='jd',
            conversation_id=raw.get('conversation_id', ''),
            shop_name=raw.get('shop_name', ''),
            customer_name=raw.get('customer_name', ''),
            customer_id=raw.get('customer_id', ''),
            employee_name=raw.get('waiter', ''),
            status=raw.get('status', 'unclosed'),
            started_at=raw.get('started_at'),
            ended_at=raw.get('ended_at'),
            raw_data=raw,
        )