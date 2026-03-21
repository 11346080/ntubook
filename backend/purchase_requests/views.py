from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer


@api_view(['GET'])
def purchaserequest_list_api(request):
    """取得所有預約請求的 JSON API 端點 / Get all purchase requests API endpoint"""
    requests = PurchaseRequest.objects.all()
    serializer = PurchaseRequestSerializer(requests, many=True)
    return Response(serializer.data)
