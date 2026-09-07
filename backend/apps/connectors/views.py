from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.tenants.middleware import TenantAwareMixin
from .models import ConnectorConfig, SyncLog
from .serializers import ConnectorConfigSerializer, SyncLogSerializer, SyncRequestSerializer
from .tasks import run_platform_sync


class ConnectorConfigViewSet(TenantAwareMixin, viewsets.ModelViewSet):
    """平台连接配置 CRUD."""
    serializer_class = ConnectorConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConnectorConfig.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


class SyncLogViewSet(TenantAwareMixin, viewsets.ReadOnlyModelViewSet):
    """同步日志查询."""
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-started_at']

    def get_queryset(self):
        return SyncLog.objects.filter(tenant=self.request.tenant)


class SyncTriggerView(TenantAwareMixin, viewsets.ViewSet):
    """手动触发同步."""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        platform = serializer.validated_data['platform']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        # Verify config exists
        try:
            config = ConnectorConfig.objects.get(
                tenant=request.tenant, platform=platform, is_active=True
            )
        except ConnectorConfig.DoesNotExist:
            return Response(
                {'error': f'平台 "{platform}" 未配置或未启用'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Trigger async sync task
        task = run_platform_sync.delay(
            tenant_id=request.tenant.id,
            platform=platform,
            config_data=config.config_data,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
        )

        return Response(
            {'task_id': task.id, 'status': 'triggered'},
            status=status.HTTP_202_ACCEPTED,
        )