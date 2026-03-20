from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Listing
from .forms import ListingCreateForm


class ListingListView(ListView):
    """刊登列表頁（含關鍵字搜尋、ISBN 篩選、價格區間、排序）"""
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 24

    def get_queryset(self):
        qs = Listing.objects.filter(
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        ).select_related(
            'book',
            'seller__profile',
            'origin_class_group__department'
        )

        # 關鍵字搜尋（書名 / 作者）
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(book__title__icontains=q) |
                Q(book__author_display__icontains=q)
            )

        # ISBN 篩選
        isbn = self.request.GET.get('isbn', '').strip()
        if isbn:
            qs = qs.filter(
                Q(book__isbn13__icontains=isbn) |
                Q(book__isbn10__icontains=isbn)
            )

        # 價格區間
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        if min_price:
            try:
                qs = qs.filter(used_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(used_price__lte=float(max_price))
            except ValueError:
                pass

        # 排序
        sort = self.request.GET.get('sort', '-created_at').strip()
        allowed_sorts = ['-created_at', 'created_at', 'used_price', '-used_price']
        if sort in allowed_sorts:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-created_at')

        return qs


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
