from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from audit.logger import SecurityLogger
from .models import UserProfile
from .rate_limiter import login_rate_limiter

def login_view(request):
    """
    User authentication login view with rate limiting, brute-force protection,
    audit logging, and open-redirect protection.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    client_ip = SecurityLogger.get_client_ip(request) or '127.0.0.1'
    redirect_to = request.POST.get('next') or request.GET.get('next') or 'dashboard'

    if request.method == 'POST':
        attempted_username = request.POST.get('username', '').strip()

        # Check rate limiting / lockout
        is_locked, remaining_sec = login_rate_limiter.is_locked_out(client_ip, attempted_username)
        if is_locked:
            SecurityLogger.log_event(
                action='LOGIN_BLOCKED_RATE_LIMIT',
                module='accounts',
                request=request,
                details={'username': attempted_username, 'remaining_seconds': remaining_sec},
                severity='warning'
            )
            messages.error(request, f"Too many failed login attempts. Access temporarily restricted. Try again in {remaining_sec} seconds.")
            form = AuthenticationForm(request)
            return render(request, 'accounts/login.html', {'form': form, 'page_title': 'Login'}, status=429)

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            login_rate_limiter.record_success(client_ip, attempted_username)

            SecurityLogger.log_event(
                action='LOGIN_SUCCESS',
                module='accounts',
                request=request,
                user=user,
                details={'username': user.username}
            )

            messages.success(request, f"Welcome back, {user.username}!")

            # Validate next URL to prevent Open Redirect
            if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                redirect_to = 'dashboard'

            return redirect(redirect_to)
        else:
            login_rate_limiter.record_failure(client_ip, attempted_username)
            SecurityLogger.log_event(
                action='LOGIN_FAILED',
                module='accounts',
                request=request,
                details={'username': attempted_username},
                severity='warning'
            )
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form, 'page_title': 'Login'})

def logout_view(request):
    """User logout view with session invalidation and audit logging."""
    if request.user.is_authenticated:
        SecurityLogger.log_event(
            action='LOGOUT',
            module='accounts',
            request=request,
            user=request.user,
            details={'username': request.user.username}
        )
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')

def register_view(request):
    """User registration view with security auditing."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            SecurityLogger.log_event(
                action='REGISTER_SUCCESS',
                module='accounts',
                request=request,
                user=user,
                details={'username': user.username}
            )
            messages.success(request, f"Account created! Welcome to Ramonet, {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration error. Please check requirements.")
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form, 'page_title': 'Register'})

@login_required
def settings_view(request):
    """User preferences & settings view. Enforces authentication."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        theme = request.POST.get('theme', 'dark-navy')
        offline_mode = request.POST.get('offline_mode') == 'on'
        profile.theme_preference = theme
        profile.offline_mode_enabled = offline_mode
        profile.save()

        SecurityLogger.log_event(
            action='SETTINGS_UPDATED',
            module='accounts',
            request=request,
            user=request.user,
            details={'theme': theme, 'offline_mode': offline_mode}
        )

        messages.success(request, "Preferences updated successfully!")
        return redirect('accounts:settings')

    return render(request, 'accounts/settings.html', {
        'profile': profile,
        'page_title': 'Settings & Preferences'
    })
