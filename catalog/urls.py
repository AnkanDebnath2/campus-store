from django.urls import path
from .views import book_detail, home, my_orders, place_order, submit_review

app_name = 'catalog'

urlpatterns = [
    path('', home, name='home'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),
    path('order/<int:book_id>/', place_order, name='place_order'),
    path('review/<int:book_id>/', submit_review, name='submit_review'),
    path('my-orders/', my_orders, name='my_orders'),
]
