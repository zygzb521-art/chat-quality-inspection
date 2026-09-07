from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'reply_interval')


class ConversationListSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True, default='')

    class Meta:
        model = Conversation
        fields = (
            'id', 'platform', 'platform_display', 'conversation_id', 'shop_name',
            'employee', 'employee_name', 'customer_name', 'status', 'status_display',
            'total_deduction', 'risk_level', 'risk_level_display',
            'message_count', 'started_at', 'has_inquiry', 'has_quote', 'has_ordered',
        )
        read_only_fields = fields


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)

    class Meta:
        model = Conversation
        fields = '__all__'