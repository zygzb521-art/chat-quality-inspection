from rest_framework import serializers
from .models import AIAnalysisResult


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisResult
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')