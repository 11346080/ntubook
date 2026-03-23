from rest_framework import serializers
from .models import Campus, ProgramType, Department, ClassGroup


class CampusSerializer(serializers.ModelSerializer):
    """校區序列化器 / Campus Serializer"""

    class Meta:
        model = Campus
        fields = ('id', 'code', 'name_zh', 'name_en', 'short_name')


class ProgramTypeSerializer(serializers.ModelSerializer):
    """學制序列化器 / Program Type Serializer"""

    class Meta:
        model = ProgramType
        fields = ('id', 'code', 'name_zh', 'name_en')


class DepartmentSerializer(serializers.ModelSerializer):
    """系所序列化器 / Department Serializer"""

    class Meta:
        model = Department
        fields = ('id', 'code', 'name_zh', 'name_en', 'campus', 'program_type')


class ClassGroupSerializer(serializers.ModelSerializer):
    """班級序列化器 / Class Group Serializer"""

    class Meta:
        model = ClassGroup
        fields = ('id', 'code', 'name_zh', 'grade_no', 'section_code', 'department', 'program_type')
