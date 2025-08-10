from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.create_user_view, name='new_user'),
    path('login/', views.login_view, name='login'),
    path('users/', views.get_all_users, name='all_users'),
    path('user/<str:pk>/', views.manage_user_data, name='manage_user_data'),
    path('profile/', views.profile_view, name='profile_view'),
    path('getotp/', views.otp_password_reset_view, name='getotp'),
    path('resetpassword/', views.password_reset_view, name='resetpassword'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]