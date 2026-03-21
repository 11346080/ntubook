from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.book_list_api, name='api-book-list'),
    path('applicabilities/', views.bookapplicability_list_api, name='api-bookapplicability-list'),
]
