from rest_framework import serializers
from .models import ConnectorConfig, SyncLog
from .registry import list_registered
from apps.conversations.models import PlatformChoices


class ConnectorConfigSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = ConnectorConfig
        fields = ('id', 'platform', 'platform_display', 'config_data', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_platform(self, value):
        registered = list_registered()
        platform_codes = [c[0] for c in PlatformChoices.choices]
        if value not in registered:
            raise serializers.ValidationError(
                f'平台 "{value}" 未注册连接器. 可用: {", ".join(registered)}'
            )
        if value not in platform_codes:
            raise serializers.ValidationError(f'平台 "{value}" 不是有效的平台选择')
        return value


class SyncLogSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = SyncLog
        fields = '__all__'
        read_only_fields = ('id', 'started_at', 'finished_at')


class SyncRequestSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=PlatformChoices.choices)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()