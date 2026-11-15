from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from matches.models import Swipe
from matches.utils import blocked_user_ids

from .forms import ProfileForm
from .models import Profile


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user, defaults={'display_name': request.user.username}
    )
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile saved.')
        return redirect('discover')
    return render(request, 'profiles/edit.html', {'form': form})


@login_required
def discover(request):
    me = getattr(request.user, 'profile', None)
    if not me or not me.date_of_birth:
        return redirect('edit_profile')

    seen_ids = Swipe.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    candidates = (
        Profile.objects.exclude(user=request.user)
        .exclude(user_id__in=seen_ids)
        .exclude(user_id__in=blocked_user_ids(request.user))
        .exclude(user__is_active=False)
        .exclude(date_of_birth__isnull=True)
        .filter(Q(looking_for='A') | Q(looking_for=me.gender))
    )
    if me.looking_for != 'A':
        candidates = candidates.filter(gender=me.looking_for)

    return render(request, 'profiles/discover.html', {'candidates': list(candidates.order_by('?')[:10])})