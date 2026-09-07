from rest_framework import serializers
from .models import TrainingMaterial


class TrainingMaterialSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True, default='')
    rule_id_code = serializers.CharField(source='rule.rule_id', read_only=True, default='')

    class Meta:
        model = TrainingMaterial
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')