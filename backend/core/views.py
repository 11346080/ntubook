from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ProgramType, Department, ClassGroup
from .serializers import ProgramTypeSerializer, DepartmentSerializer, ClassGroupSerializer


@api_view(['GET'])
def programtype_list_api(request):
    """取得所有學制的 JSON API 端點 / Get all program types API endpoint"""
    program_types = ProgramType.objects.all()
    serializer = ProgramTypeSerializer(program_types, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def department_list_api(request):
    """取得所有系所的 JSON API 端點 / Get all departments API endpoint"""
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def classgroup_list_api(request):
    """取得所有班級的 JSON API 端點 / Get all class groups API endpoint"""
    class_groups = ClassGroup.objects.all()
    serializer = ClassGroupSerializer(class_groups, many=True)
    return Response(serializer.data)
