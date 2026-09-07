from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.tenants.middleware import TenantAwareMixin
from .models import Violation
from .serializers import ViolationSerializer, ViolationReviewSerializer


class ViolationViewSet(TenantAwareMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ViolationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'rule']
    search_fields = ['conversation__customer_name']
    ordering_fields = ['created_at', 'penalty_points']
    ordering = ['-created_at']

    def get_queryset(self):
        return Violation.objects.filter(tenant=self.request.tenant)\
            .select_related('rule', 'conversation', 'employee')

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        violation = self.get_object()
        serializer = ViolationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']

        status_map = {
            'confirm': 'confirmed',
            'appeal': 'appealed',
            'close': 'closed',
        }
        violation.status = status_map[action_type]
        violation.reviewed_by = request.user
        violation.review_notes = serializer.validated_data.get('review_notes', '')
        if serializer.validated_data.get('adjusted_penalty') is not None:
            violation.adjusted_penalty = serializer.validated_data['adjusted_penalty']
        violation.reviewed_at = timezone.now()
        violation.save()

        return Response(ViolationSerializer(violation).data)