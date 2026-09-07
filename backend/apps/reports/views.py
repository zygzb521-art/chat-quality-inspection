from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.tenants.middleware import TenantAwareMixin
from .models import Report
from .serializers import ReportListSerializer, ReportDetailSerializer
from .tasks import generate_and_push_daily_report


class ReportViewSet(TenantAwareMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(tenant=self.request.tenant)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReportDetailSerializer
        return ReportListSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        from .generator import generate_daily_report
        report = generate_daily_report(request.tenant)
        return Response(ReportDetailSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def push(self, request, pk=None):
        report = self.get_object()
        from .push import push_to_feishu, push_to_weixin
        pushed = push_to_feishu(report) or push_to_weixin(report)
        if pushed:
            report.status = 'sent'
            report.save(update_fields=['status'])
            return Response({'status': 'sent'})
        return Response({'error': '推送失败'}, status=400)