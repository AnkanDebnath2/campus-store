from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import SignupForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:home')

    if request.method == 'POST' and request.POST.get('form_type') == 'login':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('catalog:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    signup_form = SignupForm()
    return render(request, 'accounts/login.html', {
        'login_form': form,
        'signup_form': signup_form,
        'active_tab': 'login'
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:home')

    if request.method == 'POST' and request.POST.get('form_type') == 'signup':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Campus Store, {user.username}!")
            return redirect('catalog:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    login_form = AuthenticationForm()
    return render(request, 'accounts/login.html', {
        'login_form': login_form,
        'signup_form': form,
        'active_tab': 'signup'
    })


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')
