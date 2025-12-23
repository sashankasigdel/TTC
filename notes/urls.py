# notes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.universal_page, name='home'),
    path('login/', views.simple_login, name='login'),
    path('logout/', views.simple_logout, name='logout'),
    path('<str:page_name>/', views.universal_page, name='page'),
]