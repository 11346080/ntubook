from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from .models import PurchaseRequest


# =============================================================================
# 預約請求列表（會員視角：買家視角 + 賣家視角合併一頁）
# GET ?role=buyer  ?role=seller  ?role= (預設顯示兩者)
# =============================================================================
class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'purchase_requests/request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        role = self.request.GET.get('role', '')
        user = self.request.user
        if role == 'buyer':
            return PurchaseRequest.objects.filter(buyer=user).select_related(
                'listing__book', 'listing__seller__profile'
            )
        elif role == 'seller':
            return PurchaseRequest.objects.filter(
                listing__seller=user
            ).select_related('listing__book', 'buyer__profile')
        # default: 我的請求（買家視角）
        return PurchaseRequest.objects.filter(buyer=user).select_related(
            'listing__book', 'listing__seller__profile'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_role'] = self.request.GET.get('role', 'buyer')
        # 賣家視角：收到的請求
        ctx['seller_requests'] = PurchaseRequest.objects.filter(
            listing__seller=self.request.user
        ).select_related('listing__book', 'buyer__profile')[:10]
        return ctx


# =============================================================================
# 預約請求詳情
# =============================================================================
class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'purchase_requests/request_detail.html'
    context_object_name = 'purchase_request'

    def get_queryset(self):
        return PurchaseRequest.objects.filter(
            buyer=self.request.user
        ) | PurchaseRequest.objects.filter(
            listing__seller=self.request.user
        )


# =============================================================================
# 接受請求（僅賣家可操作）
# =============================================================================
def accept_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    if pr.listing.seller != request.user:
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')
    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法接受。')
        return redirect('purchase_requests:request_list')

    pr.status = PurchaseRequest.Status.ACCEPTED
    pr.responded_at = timezone.now()
    pr.contact_released_at = timezone.now()
    pr.save(update_fields=['status', 'responded_at', 'contact_released_at', 'updated_at'])

    # 保留刊登
    pr.listing.status = 'RESERVED'
    pr.listing.save(update_fields=['status', 'updated_at'])

    messages.success(request, f'已接受預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')


# =============================================================================
# 拒絕請求（僅賣家可操作）
# =============================================================================
def reject_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    if pr.listing.seller != request.user:
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')
    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法拒絕。')
        return redirect('purchase_requests:request_list')

    pr.status = PurchaseRequest.Status.REJECTED
    pr.responded_at = timezone.now()
    pr.save(update_fields=['status', 'responded_at', 'updated_at'])

    messages.info(request, f'已拒絕預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')


# =============================================================================
# 取消請求（買家或賣家）
# =============================================================================
def cancel_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    role = request.GET.get('role', 'buyer')
    is_buyer = (pr.buyer == request.user)
    is_seller = (pr.listing.seller == request.user)

    if not (is_buyer or is_seller):
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')

    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法取消。')
        return redirect('purchase_requests:request_list')

    if is_buyer:
        pr.status = PurchaseRequest.Status.CANCELLED_BY_BUYER
    else:
        pr.status = PurchaseRequest.Status.CANCELLED_BY_SELLER
        # 取消時：若為賣家取消，且刊登是 RESERVED，則恢復為 AVAILABLE
        if pr.listing.status == 'RESERVED':
            pr.listing.status = 'AVAILABLE'
            pr.listing.save(update_fields=['status', 'updated_at'])

    pr.save(update_fields=['status', 'updated_at'])
    messages.info(request, f'已取消預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')
