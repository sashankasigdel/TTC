# notes/views.py - COMPLETE FILE
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .email_utils import send_otp_email  # ADD THIS IMPORT
from django.contrib.auth.decorators import user_passes_test
import logging

logger = logging.getLogger(__name__)

# ========== EXISTING FUNCTIONS (KEEP THESE) ==========
def universal_page(request, page_name=None):
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
            
            # Check email verification
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
# notes/views.py - Update register_view
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