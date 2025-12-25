# notes/views.py
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User  # ADD THIS IMPORT
from .forms import SimpleRegistrationForm

def universal_page(request, page_name=None):
    if not page_name:
        page_name = 'index'
    
    try:
        return render(request, f'{page_name}.html')
    except:
        raise Http404(f"Page '{page_name}' not found")

def register_view(request):
    """Simple user registration - just username and password"""
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # DON'T use form.save() directly - it might not hash password properly
                # Instead, create user manually
                username = form.cleaned_data['username']
                password1 = form.cleaned_data['password1']
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists. Please choose another.')
                    return render(request, 'register.html', {'form': form})
                
                # Create user with create_user() - THIS HASHS PASSWORD PROPERLY
                user = User.objects.create_user(
                    username=username,
                    password=password1  # This automatically hashes the password
                )
                
                print(f"DEBUG: User created - ID: {user.id}, Username: {user.username}")
                print(f"DEBUG: Password hash: {user.password[:50]}...")
                print(f"DEBUG: Is hashed? {user.password.startswith('pbkdf2_sha256$')}")
                
                # Auto-login after registration
                login(request, user)
                messages.success(request, f'Welcome to The Tuition Class, {user.username}!')
                return redirect('home')
                
            except Exception as e:
                print(f"DEBUG: Error creating user: {str(e)}")
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Form validation failed
            print(f"DEBUG: Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SimpleRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login view with Google option"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"DEBUG: Login attempt - Username: '{username}'")
        
        # Check if user exists first
        user_exists = User.objects.filter(username=username).exists()
        print(f"DEBUG: User exists in DB? {user_exists}")
        
        if user_exists:
            user = User.objects.get(username=username)
            print(f"DEBUG: Found user - ID: {user.id}")
            print(f"DEBUG: Password hash: {user.password[:50]}...")
        
        user = authenticate(request, username=username, password=password)
        print(f"DEBUG: Authenticate result: {user}")
        
        if user is not None:
            login(request, user)
            
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')