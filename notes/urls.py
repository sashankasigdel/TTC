# notes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.universal_page, {'page_name': 'index'}, name='home'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Email verification
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    
    # Universal pages
    path('<str:page_name>/', views.universal_page, name='universal_page'),
]