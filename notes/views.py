# notes/views.py
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, f'Welcome to The Tuition Class, {user.username}!')
            return redirect('home')
    else:
        form = SimpleRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login view with Google option"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
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
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')