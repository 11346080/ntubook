from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """檢舉案件序列化器 / Report Serializer"""

    class Meta:
        model = Report
        fields = '__all__'
