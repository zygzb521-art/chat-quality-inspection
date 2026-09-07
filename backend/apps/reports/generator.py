import logging
from datetime import timedelta
from django.db.models import Count, Sum, Avg
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_daily_report(tenant):
    """Generate a daily report for the given tenant (yesterday's data by default)."""
    from .models import Report
    from apps.conversations.models import Conversation
    from apps.reviews.models import Violation
    from apps.rules.models import Rule

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    report, created = Report.objects.get_or_create(
        tenant=tenant,
        report_date=yesterday.date(),
    )

    # Conversations
    convs = Conversation.objects.filter(
        tenant=tenant, started_at__gte=yesterday, started_at__lt=today,
    )
    total = convs.count()
    high_risk = convs.filter(risk_level='high').count()
    avg_deduction = convs.aggregate(avg=Avg('total_deduction'))['avg'] or 0

    # Violations
    violations = Violation.objects.filter(
        tenant=tenant, created_at__gte=yesterday, created_at__lt=today,
    )
    v_count = violations.count()
    total_penalty = violations.aggregate(s=Sum('penalty_points'))['s'] or 0

    # Employee rankings
    rankings = violations.values(
        'employee__first_name', 'employee__last_name',
    ).annotate(
        count=Count('id'),
        penalty=Sum('penalty_points'),
    ).order_by('-penalty')[:20]

    employee_rankings = [
        {
            'name': f'{r["employee__last_name"] or ""}{r["employee__first_name"] or ""}',
            'count': r['count'],
            'penalty': r['penalty'],
        }
        for r in rankings if r.get('employee__first_name') or r.get('employee__last_name')
    ]

    # Rule distribution
    dist = violations.values('rule__rule_id', 'rule__name').annotate(
        count=Count('id'),
    ).order_by('-count')

    # High risk sessions
    high_risk_list = convs.filter(risk_level='high').values(
        'customer_name', 'total_deduction', 'platform',
    )[:10]

    # Update report
    report.total_conversations = total
    report.violation_count = v_count
    report.total_penalty = total_penalty
    report.high_risk_count = high_risk
    report.avg_score = round(max(0, 100 - avg_deduction), 1)
    report.employee_rankings = employee_rankings
    report.rule_distribution = list(dist)
    report.high_risk_sessions = list(high_risk_list)
    report.save()

    logger.info('Report generated for %s: %d convs, %d violations',
                yesterday.date(), total, v_count)
    return report