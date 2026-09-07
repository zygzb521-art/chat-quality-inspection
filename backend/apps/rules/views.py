from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RuleCategory, Rule
from .serializers import RuleCategorySerializer, RuleSerializer


class RuleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleCategory.objects.all()
    serializer_class = RuleCategorySerializer
    permission_classes = [IsAuthenticated]


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all().select_related('category')
    serializer_class = RuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'rule_type', 'is_active']
    ordering = ['sort_order']