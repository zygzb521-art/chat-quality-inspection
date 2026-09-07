from rest_framework import serializers
from .models import Report


class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'report_date', 'total_conversations', 'violation_count',
                  'total_penalty', 'avg_score', 'status', 'created_at')


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'