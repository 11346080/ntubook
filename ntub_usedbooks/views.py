from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from listings.models import Listing


def home(request):
    latest_listings = []
    try:
        latest_listings = list(
            Listing.objects.filter(
                status=Listing.Status.AVAILABLE,
                deleted_at__isnull=True
            ).select_related(
                'book', 'seller__profile'
            ).order_by('-created_at')[:8]
        )
    except Exception:
        pass
    return render(request, "index.html", {'latest_listings': latest_listings})


# =============================================================================
# 管理員儀表板（自訂頁面，非 Django admin 內建）
# =============================================================================
def admin_dashboard(request):
    """自訂管理員儀表板頁面 — /admin/dashboard/"""
    if not (request.user.is_authenticated and request.user.is_staff):
        return render(request, "admin/dashboard.html")

    from accounts.models import User
    from listings.models import Listing
    from moderation.models import Report

    seven_days_ago = timezone.now() - timedelta(days=7)

    ctx = {
        'active_section': request.GET.get('section', 'overview'),
        'total_users': User.objects.count(),
        'total_listings': Listing.objects.count(),
        'active_listings': Listing.objects.filter(status=Listing.Status.AVAILABLE).count(),
        'open_reports': Report.objects.filter(
            status__in=['OPEN', 'IN_REVIEW']
        ).count(),
        'new_listings_7d': Listing.objects.filter(created_at__gte=seven_days_ago).count(),
        'sold_count': Listing.objects.filter(status=Listing.Status.SOLD).count(),
        'suspended_users': User.objects.filter(account_status='SUSPENDED').count(),
    }
    return render(request, "admin/dashboard.html", ctx)
