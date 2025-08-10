from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.display, name='display'),
    path('room/', views.new_room, name='create_new_room'),
    path('rooms/', views.get_all_rooms, name='get_all_rooms'),
    path('room/<str:room_no>/', views.access_room_by_room_no, name='get_by_room_no'),
    path('rooms/available', views.search_available_rooms, name='search_available_room'),
    path('room/check_timeframe', views.check_room_availability_within_timeframe, name='check_timeframe'),
    path('room/changeroomavailability', views.changeroomavailability, name='changeroomavailability'),
]