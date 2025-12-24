# notes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.universal_page, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<str:page_name>/', views.universal_page, name='page'),
]