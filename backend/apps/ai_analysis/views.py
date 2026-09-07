from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.tenants.middleware import TenantAwareMixin
from .models import AIAnalysisResult
from .serializers import AIAnalysisResultSerializer


class AIAnalysisResultViewSet(TenantAwareMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AIAnalysisResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AIAnalysisResult.objects.filter(tenant=self.request.tenant)\
            .select_related('conversation')

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({'error': 'conversation_id required'}, status=400)

        from .tasks import analyze_conversation_ai
        analyze_conversation_ai.delay(conversation_id)

        return Response({'status': 'queued'}, status=status.HTTP_202_ACCEPTED)