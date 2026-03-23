from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Campus, ProgramType, Department, ClassGroup
from .serializers import CampusSerializer, ProgramTypeSerializer, DepartmentSerializer, ClassGroupSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def campus_list_api(request):
    """
    取得所有校區的 JSON API 端點 / Get all campuses API endpoint
    公開存取 / Public access
    """
    campuses = Campus.objects.filter(is_active=True).order_by('sort_order', 'code')
    serializer = CampusSerializer(campuses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def programtype_list_api(request):
    """
    取得所有學制的 JSON API 端點 / Get all program types API endpoint
    公開存取 / Public access
    """
    program_types = ProgramType.objects.filter(is_active=True).order_by('sort_order', 'code')
    serializer = ProgramTypeSerializer(program_types, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def department_list_api(request):
    """
    取得系所列表 JSON API 端點，支援篩選 / Get departments with optional filtering
    
    支援的參數:
    - campus_id: 校區 ID (若資料庫中 campus 為 NULL，該筆資料在所有校區都會顯示)
    - program_type_id: 學制 ID
    
    業務邏輯:
    - 若 campus 為 NULL，該系所屬於所有校區（跨校區系所）
    - 若 campus 有值，則該系所僅屬於該特定校區
    
    公開存取 / Public access
    """
    from django.db.models import Q
    
    departments = Department.objects.filter(is_active=True)
    
    # 支援按學制篩選（優先）
    program_type_id = request.query_params.get('program_type_id')
    if program_type_id:
        departments = departments.filter(program_type_id=program_type_id)
    
    # 支援按校區篩選 - 邏輯：campus=該校區 OR campus=NULL（跨校區）
    campus_id = request.query_params.get('campus_id')
    if campus_id:
        departments = departments.filter(
            Q(campus_id=campus_id) | Q(campus__isnull=True)
        )
    
    departments = departments.order_by('code')
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def classgroup_list_api(request):
    """
    取得班級列表 JSON API 端點，支援篩選 / Get class groups with optional filtering
    
    支援的參數:
    - department_id: 系所 ID
    
    公開存取 / Public access
    """
    class_groups = ClassGroup.objects.filter(is_active=True)
    
    # 支援按系所篩選
    department_id = request.query_params.get('department_id')
    if department_id:
        class_groups = class_groups.filter(department_id=department_id)
    
    class_groups = class_groups.order_by('code')
    serializer = ClassGroupSerializer(class_groups, many=True)
    return Response(serializer.data)
