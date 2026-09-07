import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from .models import SyncLog
from .registry import get_connector

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def run_platform_sync(self, tenant_id: int, platform: str,
                      config_data: dict, start_time: str, end_time: str):
    """拉取指定平台在时间范围内的聊天记录并入库."""
    from apps.tenants.models import Tenant
    from apps.accounts.models import User
    from apps.conversations.models import Conversation, Message

    sync_log = SyncLog.objects.create(
        tenant_id=tenant_id, platform=platform, status='running'
    )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
        connector = get_connector(platform, config_data)

        st = datetime.fromisoformat(start_time)
        et = datetime.fromisoformat(end_time)
        if timezone.is_naive(st):
            st = timezone.make_aware(st)
        if timezone.is_naive(et):
            et = timezone.make_aware(et)

        results = connector.sync(st, et)

        conv_count = 0
        msg_count = 0

        for conn_conv in results:
            # Try to match employee by name or platform account
            employee = User.objects.filter(
                tenant_id=tenant_id,
                platform_accounts__contains={platform: conn_conv.employee_name},
            ).first()

            defaults = {
                'tenant': tenant,
                'platform': conn_conv.platform,
                'shop_name': conn_conv.shop_name,
                'customer_name': conn_conv.customer_name,
                'customer_id': conn_conv.customer_id,
                'employee': employee,
                'status': conn_conv.status,
                'order_amount': conn_conv.order_amount,
                'has_inquiry': conn_conv.has_inquiry,
                'has_quote': conn_conv.has_quote,
                'has_ordered': conn_conv.has_ordered,
                'has_paid': conn_conv.has_paid,
                'started_at': conn_conv.started_at,
                'ended_at': conn_conv.ended_at,
                'raw_data': conn_conv.raw_data,
            }

            conv, created = Conversation.objects.update_or_create(
                tenant=tenant,
                platform=conn_conv.platform,
                conversation_id=conn_conv.conversation_id,
                defaults=defaults,
            )

            if created or conn_conv.messages:
                # Delete existing messages if re-syncing, then bulk create
                if not created:
                    Message.objects.filter(conversation=conv).delete()

                msg_objs = [
                    Message(
                        tenant=tenant,
                        conversation=conv,
                        direction=m.direction,
                        sender_name=m.sender_name,
                        content=m.content,
                        sent_at=m.sent_at,
                        msg_sequence=m.msg_sequence,
                        is_ai_generated=m.is_ai_generated,
                        metadata=m.metadata,
                    )
                    for m in conn_conv.messages
                ]
                if msg_objs:
                    Message.objects.bulk_create(msg_objs)
                    msg_count += len(msg_objs)

                conv.message_count = len(msg_objs)
                conv.save(update_fields=['message_count'])

            conv_count += 1

        sync_log.status = 'success'
        sync_log.conversations_pulled = conv_count
        sync_log.messages_pulled = msg_count
        sync_log.finished_at = timezone.now()
        sync_log.save()

        logger.info('Sync %s: %d convs, %d msgs in %dms',
                    platform, conv_count, msg_count,
                    (sync_log.finished_at - sync_log.started_at).total_seconds())

    except Exception as e:
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        sync_log.finished_at = timezone.now()
        sync_log.save()
        logger.exception('Sync %s failed: %s', platform, e)
        raise self.retry(exc=e)


@shared_task
def daily_platform_sync():
    """每日定时同步：遍历所有启用的平台配置，拉取前24小时的聊天记录."""
    from .models import ConnectorConfig

    end_time = timezone.now()
    start_time = end_time - timedelta(hours=24)

    configs = ConnectorConfig.objects.filter(is_active=True).select_related('tenant')
    if not configs:
        logger.info('daily_platform_sync: no active connector configs found')
        return

    for cfg in configs:
        run_platform_sync.delay(
            tenant_id=cfg.tenant_id,
            platform=cfg.platform,
            config_data=cfg.config_data,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
        )
        logger.info('daily_platform_sync: queued %s for tenant %d', cfg.platform, cfg.tenant_id)