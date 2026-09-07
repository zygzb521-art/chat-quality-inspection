import logging
from datetime import datetime
from .base import BaseConnector, ConnectorConversation
from .registry import register_connector

logger = logging.getLogger(__name__)


@register_connector('yunke')
class YunkeConnector(BaseConnector):
    """云客CRM 聊天记录采集连接器.

    云客CRM提供HTTP API接口拉取聊天记录.
    需联系云客开通API权限.

    Config:
        api_key: 云客API Key
        api_secret: 云客API Secret
        base_url: 云客API地址 (默认 https://api.yingke.com)
    """

    def authenticate(self) -> bool:
        required = ['api_key', 'api_secret']
        if not all(self.config.get(k) for k in required):
            logger.error('Yunke auth failed: missing api_key or api_secret')
            return False
        self._auth_result = {k: self.config[k] for k in required}
        return True

    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        # TODO: call yunke conversation list API
        logger.info('Yunke pull_conversations: %s ~ %s', start_time, end_time)
        return []

    def pull_messages(self, conversation_id: str) -> list[dict]:
        # TODO: call yunke message list API
        logger.info('Yunke pull_messages: %s', conversation_id)
        return []

    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        return ConnectorConversation(
            platform='yunke',
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