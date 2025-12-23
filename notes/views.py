# notes/views.py
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import os
from django.conf import settings

def universal_page(request, page_name=None):
    """
    ONE VIEW TO HANDLE ALL PAGES!
    Access any page at: /page-name/
    """
    if not page_name:
        page_name = 'index'
    
    # Try to find the HTML file
    possible_filenames = [
        f"{page_name}.html",
        f"{page_name.upper()}.html", 
        f"{page_name.lower()}.html",
        f"G{page_name}.html",
        f"{page_name.replace('-', ' ')}.html",
    ]
    
    # Check in multiple possible locations
    for filename in possible_filenames:
        # Try direct render first (Django will look in templates folder)
        try:
            return render(request, filename)
        except:
            continue
    
    raise Http404(f"Page '{page_name}' not found")

def simple_login(request):
    """Simple login that sends admins to admin panel, users stay on site"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # If user is admin/staff, go to admin panel
            if user.is_staff:
                return redirect('/admin/')
            else:
                # Regular user goes back to home page
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    # Render login page
    return render(request, 'login.html')

def simple_logout(request):
    """Simple logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')