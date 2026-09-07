from datetime import timedelta, date
from collections import defaultdict
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.tenants.middleware import TenantAwareMixin
from apps.conversations.models import Conversation
from apps.reviews.models import Violation
from apps.rules.models import Rule


class DashboardStatsView(TenantAwareMixin, APIView):
    """看板核心指标聚合."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = request.tenant
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)

        # Today's stats
        today_convs = Conversation.objects.filter(tenant=tenant, started_at__gte=today)
        today_violations = Violation.objects.filter(
            tenant=tenant, created_at__gte=today,
        )
        pending_violations = Violation.objects.filter(
            tenant=tenant, status='pending',
        )

        # Trends — last 7 days
        daily_stats = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            next_day = day + timedelta(days=1)
            day_convs = Conversation.objects.filter(
                tenant=tenant, started_at__gte=day, started_at__lt=next_day,
            )
            day_violations = Violation.objects.filter(
                tenant=tenant, created_at__gte=day, created_at__lt=next_day,
            )
            daily_stats.append({
                'date': day.strftime('%m-%d'),
                'conversations': day_convs.count(),
                'violations': day_violations.count(),
            })

        # Distribution by rule category
        dist = Violation.objects.filter(tenant=tenant, created_at__gte=week_ago)\
            .values('rule__category__name')\
            .annotate(count=Count('id'))\
            .values('rule__category__name', 'count')

        # Recent violations
        recent = Violation.objects.filter(tenant=tenant)\
            .select_related('rule', 'conversation', 'employee')\
            .order_by('-created_at')[:10]

        recent_data = [{
            'id': v.id,
            'rule_name': v.rule.name,
            'rule_id': v.rule.rule_id,
            'customer_name': v.conversation.customer_name,
            'employee_name': v.employee.get_full_name() if v.employee else '',
            'penalty': v.adjusted_penalty or v.penalty_points,
            'status': v.status,
            'status_display': v.get_status_display(),
            'created_at': v.created_at.strftime('%m-%d %H:%M'),
        } for v in recent]

        # Avg score: 100 - avg_deduction per conversation
        avg_deduction = Conversation.objects.filter(
            tenant=tenant, started_at__gte=week_ago,
        ).aggregate(avg=Avg('total_deduction'))['avg'] or 0

        return Response({
            'today_total': today_convs.count(),
            'today_violations': today_violations.count(),
            'pending_count': pending_violations.count(),
            'avg_score': max(0, round(100 - avg_deduction, 1)),
            'trend': daily_stats,
            'distribution': list(dist),
            'recent_violations': recent_data,
        })


class RankingView(TenantAwareMixin, APIView):
    """员工排名 — 按扣分/违规数排名."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = request.tenant
        period = request.query_params.get('period', 'week')  # week / month / all

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if period == 'week':
            since = today - timedelta(days=7)
        elif period == 'month':
            since = today - timedelta(days=30)
        else:
            since = None

        qs = Violation.objects.filter(tenant=tenant)
        if since:
            qs = qs.filter(created_at__gte=since)

        rankings = qs.values('employee', 'employee__first_name', 'employee__last_name')\
            .annotate(
                violation_count=Count('id'),
                total_penalty=Sum('penalty_points'),
            )\
            .order_by('-total_penalty')[:50]

        data = []
        for i, r in enumerate(rankings, 1):
            if not r['employee']:
                continue
            data.append({
                'rank': i,
                'employee_id': r['employee'],
                'name': f'{r["employee__last_name"] or ""}{r["employee__first_name"] or ""}',
                'violation_count': r['violation_count'],
                'total_penalty': r['total_penalty'],
            })

        return Response(data)