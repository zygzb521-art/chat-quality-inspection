import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


def _format_messages(messages) -> str:
    """Format Message queryset into a readable conversation transcript."""
    lines = []
    for m in messages.order_by('sent_at'):
        role = '客服' if m.direction == 'agent' else '客户' if m.direction == 'customer' else '系统'
        lines.append(f'{role} ({m.sent_at.strftime("%H:%M")}): {m.content}')
    return '\n'.join(lines)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def analyze_conversation_ai(self, conversation_id: int):
    """Run all AI analyses on a conversation (attitude + skill + suggestions)."""
    from apps.conversations.models import Conversation
    from .models import AIAnalysisResult
    from .llm_client import LLMClient

    conv = Conversation.objects.prefetch_related('messages').get(id=conversation_id)
    messages_text = _format_messages(conv.messages.all())

    result, _ = AIAnalysisResult.objects.get_or_create(
        tenant=conv.tenant, conversation=conv,
        defaults={'status': 'pending'},
    )

    client = LLMClient()
    if not client.api_key:
        result.status = 'failed'
        result.save(update_fields=['status'])
        return

    # Attitude analysis
    try:
        attitude = client.analyze_attitude(messages_text)
        if attitude:
            result.attitude_score = attitude.get('score')
            result.attitude_detail = attitude
    except Exception as e:
        logger.error('Attitude analysis failed for conv %d: %s', conversation_id, e)

    # Skill analysis
    try:
        skill = client.analyze_skill(messages_text)
        if skill:
            result.skill_score = skill.get('score')
            result.skill_detail = skill
    except Exception as e:
        logger.error('Skill analysis failed for conv %d: %s', conversation_id, e)

    # Get violations for context
    violations_list = list(
        conv.violations.values('rule__rule_id', 'rule__name', 'penalty_points')[:10]
    )
    violations_text = '\n'.join(
        f'{v["rule__rule_id"]} {v["rule__name"]} (-{v["penalty_points"]})'
        for v in violations_list
    ) or '无'

    # Suggestions
    try:
        suggestion = client.generate_suggestions(messages_text, violations_text)
        if suggestion:
            result.suggestions = suggestion.get('suggestions', [])
            result.ai_suggestion_text = '\n'.join(suggestion.get('suggestions', []))
            result.raw_response = suggestion
    except Exception as e:
        logger.error('Suggestion generation failed for conv %d: %s', conversation_id, e)

    result.status = 'completed'
    result.save()

    # Update conversation ai_suggestion field
    if result.ai_suggestion_text:
        conv.ai_suggestion = result.ai_suggestion_text
        conv.save(update_fields=['ai_suggestion'])

    logger.info('AI analysis complete for conversation %d', conversation_id)


@shared_task
def batch_ai_analysis(hours: int = 24):
    """Batch AI analysis for recent conversations that have violations."""
    from apps.conversations.models import Conversation

    cutoff = timezone.now() - timezone.timedelta(hours=hours)
    convs = Conversation.objects.filter(
        started_at__gte=cutoff,
        total_deduction__gt=0,
    ).values_list('id', flat=True)

    count = 0
    for cid in convs:
        analyze_conversation_ai.delay(cid)
        count += 1

    logger.info('Queued AI analysis for %d conversations', count)
    return count