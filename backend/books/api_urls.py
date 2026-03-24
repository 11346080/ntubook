from django.urls import path
from . import views

urlpatterns = [
    # 書籍列表和詳情
    path('', views.book_list_api, name='api-books-list'),
    path('list/', views.book_list_api, name='api-book-list'),
    
    # 書籍適用性
    path('applicabilities/', views.bookapplicability_list_api, name='api-bookapplicability-list'),
    
    # 收藏相關
    path('favorites/', views.user_favorites_api, name='api-favorites-list'),
    path('<int:book_id>/favorite/', views.favorite_toggle_api, name='api-toggle-favorite'),
]
