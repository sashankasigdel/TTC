# notes/urls.py - EVEN SIMPLER
from django.urls import path
from . import views

urlpatterns = [
    # Home - using universal_page with explicit 'index'
    path('', views.home_view, name='home'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Email verification
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    
# ============================================================================
    # DYNAMIC COURSE URLs
    # ============================================================================
    path('courses/', views.courses_page, name='courses_page'),
    path('courses/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/<slug:subject_slug>/', views.subject_detail, name='subject_detail'),
    path('courses/<slug:course_slug>/<slug:subject_slug>/<slug:chapter_slug>/', 
         views.chapter_detail, name='chapter_detail'),

     path('courses/<slug:course_slug>/<slug:subject_slug>/<slug:chapter_slug>/study/', 
         views.study_chapter, name='study_chapter'),

     path('premium/', views.premium, name='premium'),
     path('profile/', views.user_profile, name='user_profile'),
     
     path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Universal pages for everything else
    path('<str:page_name>/', views.universal_page, name='universal_page'),
]