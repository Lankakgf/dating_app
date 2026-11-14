from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignupForm


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('edit_profile')
    return render(request, 'users/signup.html', {'form': form})