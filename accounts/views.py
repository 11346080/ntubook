from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/dashboard.html')


# W4: 添加自訂 View 到 Admin Site - Admin Dashboard
# 使用 @staff_member_required 裝飾器確保只有管理員可訪問
@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(View):
    """
    自定義 Admin Dashboard
    W4 要求：添加自訂的 View 到 Admin Site
    """
    def get(self, request):
        from listings.models import Listing
        from books.models import Book
        from notifications.models import Notification
        from purchase_requests.models import PurchaseRequest
        from accounts.models import CustomUser

        # 基本統計
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(account_status='ACTIVE').count()
        total_books = Book.objects.count()
        total_listings = Listing.objects.count()
        published_listings = Listing.objects.filter(status='PUBLISHED').count()
        sold_listings = Listing.objects.filter(status='SOLD').count()
        total_requests = PurchaseRequest.objects.count()
        unread_notifications = Notification.objects.filter(is_read=False).count()

        context = {
            'title': '儀表板',
            'total_users': total_users,
            'active_users': active_users,
            'total_books': total_books,
            'total_listings': total_listings,
            'published_listings': published_listings,
            'sold_listings': sold_listings,
            'total_requests': total_requests,
            'unread_notifications': unread_notifications,
        }
        return render(request, 'admin/dashboard.html', context)
