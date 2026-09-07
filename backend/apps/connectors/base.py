from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class ConnectorMessage:
    direction: str  # agent / customer / system
    sender_name: str
    content: str
    sent_at: datetime
    msg_sequence: int = 0
    is_ai_generated: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class ConnectorConversation:
    platform: str
    conversation_id: str
    shop_name: str = ''
    customer_name: str = ''
    customer_id: str = ''
    employee_name: str = ''
    employee_id: str = ''
    status: str = 'unclosed'
    order_amount: Optional[float] = None
    has_inquiry: bool = False
    has_quote: bool = False
    has_ordered: bool = False
    has_paid: bool = False
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    raw_data: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)


class BaseConnector(ABC):
    """Abstract base class for all platform connectors.

    Subclasses must implement authenticate(), pull_conversations(),
    pull_messages(), and normalize(). The sync() method provides
    the default orchestration flow.
    """

    def __init__(self, config: dict):
        self.config = config
        self._auth_result = None

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate against the platform API using self.config.
        Return True if successful."""
        ...

    @abstractmethod
    def pull_conversations(self, start_time: datetime, end_time: datetime) -> list[dict]:
        """Fetch raw conversation list from the platform API.
        Return list of raw dicts."""
        ...

    @abstractmethod
    def pull_messages(self, conversation_id: str) -> list[dict]:
        """Fetch raw messages for a single conversation.
        Return list of raw dicts."""
        ...

    @abstractmethod
    def normalize_conversation(self, raw: dict) -> ConnectorConversation:
        """Convert a raw conversation dict into the normalized format."""
        ...

    def normalize_message(self, raw: dict) -> ConnectorMessage:
        """Convert a raw message dict into the normalized format.
        Override if platform-specific mapping is needed."""
        return ConnectorMessage(
            direction=raw.get('direction', 'customer'),
            sender_name=raw.get('sender_name', ''),
            content=raw.get('content', ''),
            sent_at=raw.get('sent_at', datetime.now()),
            msg_sequence=raw.get('msg_sequence', 0),
            is_ai_generated=raw.get('is_ai_generated', False),
            metadata=raw.get('metadata', {}),
        )

    def sync(self, start_time: datetime, end_time: datetime) -> list[ConnectorConversation]:
        """Default sync orchestration: auth → pull → normalize.
        Returns list of normalized ConnectorConversation objects."""
        if not self.authenticate():
            raise RuntimeError(f'{self.__class__.__name__}: authentication failed')

        raw_convs = self.pull_conversations(start_time, end_time)
        result = []
        for raw_conv in raw_convs:
            conv = self.normalize_conversation(raw_conv)
            raw_msgs = self.pull_messages(conv.conversation_id)
            conv.messages = [self.normalize_message(m) for m in raw_msgs]
            result.append(conv)
        return result