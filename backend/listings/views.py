from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Listing
from .forms import ListingCreateForm
from .serializers import ListingSerializer


class ListingListView(ListView):
    """刊登列表頁"""
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return Listing.objects.filter(
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        ).select_related(
            'book',
            'seller__profile',
            'origin_class_group__department'
        ).prefetch_related('images')


class ListingDetailView(DetailView):
    """刊登詳情頁"""
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        return Listing.objects.select_related(
            'book',
            'seller__profile',
            'origin_class_group__department'
        ).prefetch_related('images')


class ListingCreateView(LoginRequiredMixin, CreateView):
    """建立刊登頁"""
    model = Listing
    form_class = ListingCreateForm
    template_name = 'listings/listing_create.html'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.status = Listing.Status.AVAILABLE
        return super().form_valid(form)


# ================= API Views =================


@api_view(['GET'])
def listing_list_api(request):
    """取得所有刊登的 JSON API 端點 / Get all listings API endpoint"""
    listings = Listing.objects.all()
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)

