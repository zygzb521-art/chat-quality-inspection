from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.tenants.middleware import TenantAwareMixin
from .models import TrainingMaterial
from .serializers import TrainingMaterialSerializer


class TrainingMaterialViewSet(TenantAwareMixin, viewsets.ModelViewSet):
    serializer_class = TrainingMaterialSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'content']
    filterset_fields = ['category', 'priority', 'rule']

    def get_queryset(self):
        return TrainingMaterial.objects.filter(tenant=self.request.tenant)\
            .select_related('rule')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)