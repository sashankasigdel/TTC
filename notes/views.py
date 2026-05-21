# notes/views.py - COMPLETE FILE
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .email_utils import send_otp_email  
from django.contrib.auth.decorators import user_passes_test
import logging
from django.shortcuts import render, get_object_or_404
from .models import Course, Subject, Chapter, Payment
from django.core.paginator import Paginator
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone

 

logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'index.html')  # your frontend index.html

# ========== EXISTING FUNCTIONS (KEEP THESE) ==========
def universal_page(request, page_name='index'):
    """Handle all pages including home"""
    if not page_name:
        page_name = 'index'
    
    try:
        return render(request, f'{page_name}.html')
    except:
        raise Http404(f"Page '{page_name}' not found")

# In login_view function - add this after successful login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check if user is staff (admin)
            if user.is_staff:
                # Admin users should go to admin panel
                messages.success(request, f'Welcome back, Admin {username}!')
                return redirect('/admin/')
            
            # Regular users continue with existing flow
            if hasattr(user, 'profile') and user.profile.email_verified:
                messages.success(request, f'Welcome back, {username}!')
            else:
                messages.warning(request, 
                    f'Welcome back! Your email is not verified. '
                    f'Please verify your email for full access.'
                )
            
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# ========== NEW EMAIL VERIFICATION FUNCTIONS ==========

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        print(f"=== REAL EMAIL REGISTRATION ===")
        print(f"Username: {username}")
        print(f"Email: {email}")
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'All fields are required')
            return render(request, 'register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'register.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            print(f"✓ User created: {user.username}")
            
            # Get profile and generate OTP
            profile = user.profile
            otp = profile.generate_otp()
            
            # SEND REAL EMAIL - NO FALLBACK
            print(f"📧 Sending real email to: {email}")
            send_otp_email(email, otp)
            
            # Store in session
            request.session['verify_user_id'] = user.id
            request.session['pending_email'] = email
            
            messages.success(request, 
                f'✅ Verification email sent to {email}! '
                f'Please check your inbox and spam folder.'
            )
            
            return redirect('verify_email')
            
        except Exception as e:
            print(f"✗ Registration failed: {str(e)}")
            
            # If email failed, delete the user
            if 'user' in locals():
                user.delete()
                print(f"✗ Deleted user due to email failure")
            
            messages.error(request, 
                f'Registration failed: {str(e)}. '
                f'Please check your email address or try again later.'
            )
    
    return render(request, 'register.html')

def verify_email_view(request):
    """Show OTP verification page"""
    user_id = request.session.get('verify_user_id')
    
    if not user_id:
        messages.error(request, 'No verification pending.')
        return redirect('register')
    
    return render(request, 'verify_email.html')

def verify_otp_view(request):
    """Verify the OTP entered by user"""
    if request.method == 'POST':
        user_id = request.session.get('verify_user_id')
        otp_entered = request.POST.get('otp', '').strip()
        
        print(f"=== OTP VERIFICATION ===")
        print(f"User ID from session: {user_id}")
        print(f"OTP entered: {otp_entered}")
        
        if not user_id:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')
        
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            print(f"User: {user.username}")
            print(f"Stored OTP: {profile.verification_otp}")
            
            if profile.verify_otp(otp_entered):
                print(f"✓ OTP verified for {user.username}")
                
                # Clear session
                if 'verify_user_id' in request.session:
                    del request.session['verify_user_id']
                if 'pending_email' in request.session:
                    del request.session['pending_email']
                
                # Login user
                login(request, user)
                messages.success(request, f'Email verified! Welcome {user.username}!')
                return redirect('home')
            else:
                print(f"✗ Invalid OTP")
                messages.error(request, 'Invalid or expired OTP. Please try again.')
                
        except Exception as e:
            print(f"✗ Error: {e}")
            messages.error(request, 'Verification failed.')
    
    return redirect('verify_email')

def resend_otp_view(request):
    """Resend OTP to user"""
    user_id = request.session.get('verify_user_id')
    
    if not user_id:
        messages.error(request, 'No verification pending')
        return redirect('register')
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Generate new OTP
        otp = profile.generate_otp()
        
        # Send email
        email_sent = send_otp_email(user.email, otp)
        
        if email_sent:
            messages.success(request, f'New verification code sent to {user.email}')
        else:
            messages.error(request, 'Failed to resend verification code')
            
    except Exception as e:
        messages.error(request, 'Error resending verification code')
    
    return redirect('verify_email')

def email_verified_required(function=None):
    """Decorator to require email verification"""
    def check_verified(user):
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.email_verified
    
    return user_passes_test(check_verified)(function) if function else user_passes_test(check_verified)

# Example usage (for future protected pages):
@email_verified_required
def protected_page(request):
    return render(request, 'protected.html')

# ============================================================================
# DYNAMIC COURSE VIEWS
# ============================================================================

# In views.py, update courses_page function
def courses_page(request):
    """Display all courses grouped by level (original floating card design)"""
    # Get all active courses
    all_courses = Course.objects.filter(is_active=True).order_by('display_order', 'title')
    
    context = {
        'courses': all_courses,
        'page_title': 'All Courses'
    }
    return render(request, 'courses/all_courses.html', context)

def course_detail(request, course_slug):
    """Display subjects for a specific course"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    subjects = course.subjects.filter(is_active=True).order_by('display_order', 'title')
    
    context = {
        'course': course,
        'subjects': subjects,
        'page_title': course.title
    }
    return render(request, 'courses/course_detail.html', context)

def subject_detail(request, course_slug, subject_slug):
    """Display chapters for a specific subject"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    subject = get_object_or_404(Subject, slug=subject_slug, course=course, is_active=True)
    chapters = subject.chapters.filter(is_active=True).order_by('display_order', 'title')
    
    # Optional: Add pagination for chapters
    paginator = Paginator(chapters, 10)  # Show 10 chapters per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'course': course,
        'subject': subject,
        'chapters': page_obj,  # Use page_obj instead of chapters
        'page_title': f"{subject.title} - {course.title}"
    }
    return render(request, 'courses/subject_detail.html', context)

def chapter_detail(request, course_slug, subject_slug, chapter_slug):
    """Display a single chapter"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    subject = get_object_or_404(Subject, slug=subject_slug, course=course, is_active=True)
    chapter = get_object_or_404(Chapter, slug=chapter_slug, subject=subject, is_active=True)
    
    context = {
        'course': course,
        'subject': subject,
        'chapter': chapter,
        'page_title': f"{chapter.title} - {subject.title}"
    }
    return render(request, 'courses/chapter_detail.html', context)

# In views.py, update your home function:
def home(request):
    """Home page with featured courses"""
    # Get first 6 active courses for featured section
    featured_courses = Course.objects.filter(is_active=True).order_by('display_order', 'title')[:6]
    
    context = {
        'featured_courses': featured_courses,
        'page_title': 'The Tuition Class - Home'
    }
    return render(request, 'index.html', context)

def study_chapter(request, course_slug, subject_slug, chapter_slug):
    """
    Enhanced PDF viewer for 'Study Chapter' button
    """
    # Get the chapter
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    subject = get_object_or_404(Subject, slug=subject_slug, course=course, is_active=True)
    chapter = get_object_or_404(Chapter, slug=chapter_slug, subject=subject, is_active=True)
    
    # Check if PDF exists
    if not chapter.pdf_file:
        messages.warning(request, "No PDF available for this chapter yet.")
        return redirect('chapter_detail', course_slug=course_slug, subject_slug=subject_slug, chapter_slug=chapter_slug)
    
    # Prepare context for template
    context = {
        'course': course,
        'subject': subject,
        'chapter': chapter,
        'pdf_url': chapter.pdf_file.url,
        'page_title': f"Study: {chapter.title}"
    }

    
    # Render the enhanced PDF viewer
    return render(request, 'courses/study_chapter.html', context)
    
# ============================================================================
# PREMIUM SUBSCRIPTION VIEW
# ============================================================================


def premium(request):
    """Premium subscription payment page"""
    # Check if already premium
    if hasattr(request.user, 'profile') and request.user.profile.is_premium:
        messages.info(request, "You already have premium access!")
        return redirect('courses_page')
    
    if request.method == 'POST':
        # Handle payment submission
        screenshot = request.FILES.get('screenshot')
        email = request.POST.get('email')

        if not screenshot:
            messages.error(request, "Please upload payment screenshot.")
            return redirect('premium')
        
        if not email:
            messages.error(request, "Please provide your email address.")
            return redirect('premium')


        # Save payment
        Payment.objects.create(
            user=request.user,
            email=email,
            screenshot=screenshot
        )
        
        messages.success(request, 
            "✅ Payment submitted! We'll verify within 24 hours."
        )
        return redirect('home')
    
    # GET request - show payment page
    context = {
        'page_title': 'Get Premium Access',
        'user': request.user,
    }
    return render(request, 'premium.html', context)

@login_required
def user_profile(request):
    """User profile page showing account information and premium status"""
    context = {
        'page_title': 'My Profile',
        'user': request.user,
    }
    return render(request, 'profile/user_profile.html', context)
    
def forgot_password(request):
    """Simple password reset - one form"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Basic validation
        if not all([username, email, new_password, confirm_password]):
            messages.error(request, "Please fill all fields")
            return render(request, 'forgot_password.html')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'forgot_password.html')
        
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, 'forgot_password.html')
        
        # Find user
        try:
            user = User.objects.get(username=username, email=email)
            
            # Update password
            user.password = make_password(new_password)
            user.save()
            
            messages.success(request, 
                "✅ Password changed successfully! You can now login with your new password."
            )
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, "Username and email do not match")
    
    return render(request, 'forgot_password.html')

@staff_member_required
def system_report(request):
    """Generate comprehensive system status report"""
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)
    
    # User Statistics
    total_users = User.objects.count()
    premium_users = User.objects.filter(profile__is_premium=True).count()
    free_users = total_users - premium_users
    new_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    active_users = User.objects.filter(last_login__gte=seven_days_ago).count()
    
    # Premium Subscriptions
    from .models import PremiumSubscription
    active_premium = PremiumSubscription.objects.filter(
        is_active=True,
        ends_at__gte=today.date()
    ).count()
    
    expiring_soon = PremiumSubscription.objects.filter(
        is_active=True,
        ends_at__gte=today.date(),
        ends_at__lte=today.date() + timedelta(days=3)
    ).count()
    
    expired_but_marked = User.objects.filter(
        profile__is_premium=True
    ).exclude(
        premium_subscriptions__is_active=True,
        premium_subscriptions__ends_at__gte=today.date()
    ).count()
    
    # Calculate average premium duration
    active_subs = PremiumSubscription.objects.filter(is_active=True)
    if active_subs.exists():
        avg_duration = active_subs.aggregate(
            avg_days=Avg('days_remaining')
        )['avg_days'] or 0
        avg_duration = round(avg_duration, 1)
    else:
        avg_duration = 0
    
    # Revenue & Payments
    from .models import Payment
    total_payments = Payment.objects.count()
    
    # Check if Payment model has 'status' field
    try:
        approved_payments = Payment.objects.filter(status='approved').count()
        pending_payments = Payment.objects.filter(status='pending').count()
    except:
        # If no status field, check via premium subscription
        approved_payments = PremiumSubscription.objects.filter(payment__isnull=False).count()
        pending_payments = Payment.objects.count() - approved_payments
    
    # Calculate revenue (assume ₹1000 per premium)
    total_revenue = approved_payments * 1000
    recent_revenue = new_users * 1000  # Simplified calculation
    
    # Course Usage (simplified - adjust based on your models)
    from .models import Course
    total_courses = Course.objects.count()
    
    context = {
        'report_date': today,
        'total_users': total_users,
        'premium_users': premium_users,
        'free_users': free_users,
        'new_users': new_users,
        'active_users': active_users,
        'active_premium': active_premium,
        'expiring_soon': expiring_soon,
        'expired_but_marked': expired_but_marked,
        'avg_duration': avg_duration,
        'total_payments': total_payments,
        'approved_payments': approved_payments,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'total_courses': total_courses,
        'premium_percentage': (premium_users / total_users * 100) if total_users > 0 else 0,
        'approval_percentage': (approved_payments / total_payments * 100) if total_payments > 0 else 0,
    }
    
    return render(request, 'admin/system_report.html', context)