from django.urls import path
from . import views

urlpatterns = [
    path('neworder/', views.place_order_view, name='place_order'),
    path('order/<str:pk>', views.manage_order_view, name='manage_order'),
    path('history/', views.order_history, name='order_history'),
    path('orders/', views.all_orders_view, name='all_orders'),
    path('search/', views.search_for_laundry_order, name='search')
]