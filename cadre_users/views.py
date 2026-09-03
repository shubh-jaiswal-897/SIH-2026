from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User

def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('officer_dashboard')
    return redirect('login')

def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('officer_dashboard')

        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, Officer {user.get_full_name() or user.username}!")
            return redirect('officer_dashboard')
        else:
            messages.error(request, "Invalid username or password. Default demo user: officer1 / pass123")
            
    return render(request, 'registration/login.html')

def user_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('login')
