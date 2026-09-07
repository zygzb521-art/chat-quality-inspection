from rest_framework import serializers
from .models import Violation, RuleTriggerLog
from apps.rules.models import Rule
from apps.conversations.models import Conversation


class ViolationSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    rule_id_code = serializers.CharField(source='rule.rule_id', read_only=True)
    platform = serializers.CharField(source='conversation.platform', read_only=True)
    customer_name = serializers.CharField(source='conversation.customer_name', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True, default='')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Violation
        fields = '__all__'
        read_only_fields = ('id', 'tenant', 'created_at', 'updated_at', 'reviewed_at')


class ViolationReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['confirm', 'appeal', 'close'])
    adjusted_penalty = serializers.IntegerField(required=False, min_value=0)
    review_notes = serializers.CharField(required=False, allow_blank=True)


class RuleTriggerLogSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    rule_id_code = serializers.CharField(source='rule.rule_id', read_only=True)

    class Meta:
        model = RuleTriggerLog
        fields = '__all__'