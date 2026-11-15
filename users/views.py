from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import SignupForm


def home(request):
    if request.user.is_authenticated:
        return redirect('discover')
    return render(request, 'users/home.html')


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('edit_profile')
    return render(request, 'users/signup.html', {'form': form})


def terms(request):
    return render(request, 'users/terms.html')


def privacy(request):
    return render(request, 'users/privacy.html')


@login_required
def account_settings(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed.')
        return redirect('account_settings')
    return render(request, 'users/settings.html', {'form': form})


@login_required
@require_POST
def delete_account(request):
    if not request.user.check_password(request.POST.get('password', '')):
        messages.error(request, 'Incorrect password. Your account was not deleted.')
        return redirect('account_settings')
    user = request.user
    profile = getattr(user, 'profile', None)
    if profile and profile.photo:
        profile.photo.delete(save=False)
    logout(request)
    user.delete()
    messages.success(request, 'Your account and data have been deleted.')
    return redirect('login')