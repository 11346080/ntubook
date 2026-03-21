from rest_framework import serializers
from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """使用者序列化器 / User Serializer"""

    class Meta:
        model = User
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """使用者檔案序列化器 / User Profile Serializer"""

    class Meta:
        model = UserProfile
        fields = '__all__'
