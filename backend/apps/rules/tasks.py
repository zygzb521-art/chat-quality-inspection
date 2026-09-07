import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def run_rule_engine_for_recent_conversations(hours: int = 24):
    """对指定小时内更新的所有会话执行规则引擎."""
    from apps.conversations.models import Conversation
    from apps.reviews.models import Violation, RuleTriggerLog
    from .engine import RuleEngine

    cutoff = timezone.now() - timezone.timedelta(hours=hours)
    conversations = Conversation.objects.filter(
        started_at__gte=cutoff,
    ).prefetch_related('messages')

    count = 0
    total_penalty = 0
    for conv in conversations:
        # Skip if already processed (has violations from this run window)
        engine = RuleEngine(conv)
        deduction = engine.apply()
        if deduction > 0:
            count += 1
            total_penalty += deduction
            logger.info('RuleEngine: %s → -%d points', conv, deduction)

    logger.info('RuleEngine complete: %d/%d conversations triggered (%d total penalty)',
                count, conversations.count(), total_penalty)
    return {'processed': conversations.count(), 'triggered': count, 'total_penalty': total_penalty}