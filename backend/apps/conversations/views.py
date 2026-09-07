from django.db import models
from rest_framework import viewsets, permissions
from django_filters import rest_framework as filters
from apps.tenants.middleware import TenantAwareMixin
from .models import Conversation, PlatformChoices
from .serializers import ConversationListSerializer, ConversationDetailSerializer


class ConversationFilter(filters.FilterSet):
    platform = filters.ChoiceFilter(choices=PlatformChoices.choices)
    status = filters.ChoiceFilter(choices=Conversation.STATUS_CHOICES)
    risk_level = filters.ChoiceFilter(choices=Conversation.RISK_CHOICES)
    employee = filters.NumberFilter()
    start_date = filters.DateTimeFromToRangeFilter(field_name='started_at')
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(customer_name__icontains=value) |
            models.Q(conversation_id__icontains=value) |
            models.Q(shop_name__icontains=value)
        )

    class Meta:
        model = Conversation
        fields = ['platform', 'status', 'risk_level', 'employee', 'start_date']


class ConversationViewSet(TenantAwareMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Conversation.objects.all()
    filterset_class = ConversationFilter
    search_fields = ['customer_name', 'conversation_id', 'shop_name']
    ordering_fields = ['started_at', 'total_deduction', 'message_count']
    ordering = ['-started_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def get_queryset(self):
        return Conversation.objects.filter(tenant=self.request.tenant)