from django.urls import path
from . import views

urlpatterns = [
    path('newservice/', views.create_laundry_service_view, name='new_service'),
    path('services/', views.all_laundry_services_view, name='get_laundry_services'),
    path('service/<str:name>', views.manage_laundryservice_view, name='manage_laundry_service'),

    path('newservicetype/', views.create_service_type_view, name='new_service_type'),
    path('servicetypes/', views.all_services_type_view, name='get_services_type'),
    path('servicetype/<str:name>', views.manage_services_type_view, name='get_service_type'),

    
    path('newgarment/', views.create_garment_view, name='new_garment'),
    path('garment/<str:name>', views.manage_garment_view, name='get_garment'),
    path('garments/', views.all_garment_view, name='view_all_garment'),

    path('newservicepricing/', views.create_service_pricing_view, name='new_servicepricing'),
    path('servicepricings/', views.all_servicepricing_view, name='view_all_servicepricing'),
    path('servicepricing/<str:name>', views.manage_services_pricing_view, name='get_service_type')
]