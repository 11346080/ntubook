from rest_framework import serializers
from .models import PurchaseRequest


class PurchaseRequestSerializer(serializers.ModelSerializer):
    """預約請求序列化器 / Purchase Request Serializer"""

    class Meta:
        model = PurchaseRequest
        fields = '__all__'
