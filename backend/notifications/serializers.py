from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器 / Notification Serializer"""

    class Meta:
        model = Notification
        fields = '__all__'
