from rest_framework import serializers
from .models import RuleCategory, Rule


class RuleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleCategory
        fields = '__all__'


class RuleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = Rule
        fields = '__all__'
        read_only_fields = ('rule_id', 'created_at')