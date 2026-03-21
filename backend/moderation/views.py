from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer


@api_view(['GET'])
def report_list_api(request):
    """取得所有檢舉案件的 JSON API 端點 / Get all reports API endpoint"""
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)
