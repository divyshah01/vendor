# core/urls.py
from django.urls import path
from .views import login_view, signup_view, logout_view, forgot_password_view
from .dashboard_views import dashboard_view
from .vendor_views import vendor_list_view, register_vendor_view, update_vendor_status_view
urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('vendors/', vendor_list_view, name='vendor_list'),
    path('vendors/register/', register_vendor_view, name='register_vendor'),
    path('vendors/status/<int:vendor_id>/', update_vendor_status_view, name='update_vendor_status'),
]
