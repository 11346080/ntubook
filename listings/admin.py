from django.contrib import admin
from .models import Listing, ListingImage, BookFavorite, PurchaseRequest

admin.site.register(Listing)
admin.site.register(ListingImage)
admin.site.register(BookFavorite)
admin.site.register(PurchaseRequest)