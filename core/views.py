from django.shortcuts import render

# Create your views here.
# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm

# core/views.py

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # 📍 FIX: Check headers for AJAX instead of using request.is_ajax()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if is_ajax or request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful as {user.get_role_display()}!")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
        
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def forgot_password_view(request):
    # Core stub for password recovery framework
    if request.method == 'POST':
        messages.info(request, "If that email exists, a password reset link has been sent.")
        return redirect('login')
    return render(request, 'auth/forgot_password.html')
