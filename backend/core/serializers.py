from rest_framework import serializers
from .models import ProgramType, Department, ClassGroup


class ProgramTypeSerializer(serializers.ModelSerializer):
    """學制序列化器 / Program Type Serializer"""

    class Meta:
        model = ProgramType
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    """系所序列化器 / Department Serializer"""

    class Meta:
        model = Department
        fields = '__all__'


class ClassGroupSerializer(serializers.ModelSerializer):
    """班級序列化器 / Class Group Serializer"""

    class Meta:
        model = ClassGroup
        fields = '__all__'
