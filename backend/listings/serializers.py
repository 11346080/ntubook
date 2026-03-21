from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    """刊登序列化器 / Listing Serializer"""

    class Meta:
        model = Listing
        fields = '__all__'
