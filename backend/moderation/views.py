from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Report
from .serializers import ReportSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def report_list_api(request):
    """
    取得所有檢舉案件的 JSON API 端點 / Get all reports API endpoint
    僅限管理員 / Admin only
    """
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)
