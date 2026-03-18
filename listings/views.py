from django.views.generic import ListView, DetailView
from .models import Listing


class ListingListView(ListView):
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return Listing.objects.filter(status='PUBLISHED', deleted_at__isnull=True).order_by('-created_at')


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        return Listing.objects.filter(status='PUBLISHED', deleted_at__isnull=True)
