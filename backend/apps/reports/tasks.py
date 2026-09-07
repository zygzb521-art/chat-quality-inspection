import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def generate_and_push_daily_report():
    """Generate daily reports for all tenants, then push."""
    from apps.tenants.models import Tenant
    from .generator import generate_daily_report
    from .push import push_to_feishu, push_to_weixin

    tenants = Tenant.objects.filter(is_active=True)
    for tenant in tenants:
        try:
            report = generate_daily_report(tenant)
            # Try push
            pushed = push_to_feishu(report) or push_to_weixin(report)
            if pushed:
                report.status = 'sent'
                report.save(update_fields=['status'])
                logger.info('Report %s pushed for tenant %s', report.report_date, tenant.slug)
        except Exception as e:
            logger.error('Report generation failed for tenant %s: %s', tenant.slug, e)