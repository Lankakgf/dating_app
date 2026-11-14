from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReportForm
from .models import Block, Match, Report, Swipe

User = get_user_model()


@login_required
@require_POST
def swipe(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if target == request.user:
        return JsonResponse({'matched': False}) if is_ajax else redirect('discover')

    liked = request.POST.get('action') == 'like'
    Swipe.objects.update_or_create(
        from_user=request.user, to_user=target, defaults={'liked': liked}
    )

    matched = False
    if liked and Swipe.objects.filter(from_user=target, to_user=request.user, liked=True).exists():
        a, b = sorted([request.user.id, target.id])
        _, created = Match.objects.get_or_create(user1_id=a, user2_id=b)
        matched = created

    profile = getattr(target, 'profile', None)
    name = profile.display_name if profile else target.username
    photo = profile.photo.url if profile and profile.photo else ''

    if is_ajax:
        return JsonResponse({'matched': matched, 'name': name, 'photo': photo})

    if matched:
        messages.success(request, f"It's a match with {name}!")
    return redirect('discover')


@login_required
def match_list(request):
    matches = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user)).select_related(
        'user1__profile', 'user2__profile'
    )
    people = [m.user2 if m.user1_id == request.user.id else m.user1 for m in matches]
    return render(request, 'matches/list.html', {'people': people})


def _block(me, target):
    Block.objects.get_or_create(blocker=me, blocked=target)
    low, high = sorted([me.id, target.id])
    Match.objects.filter(user1_id=low, user2_id=high).delete()


@login_required
@require_POST
def block_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target != request.user:
        _block(request.user, target)
        messages.success(request, 'User blocked.')
    return redirect('match_list')


@login_required
def report_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        return redirect('discover')
    form = ReportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.reported = target
        report.save()
        if form.cleaned_data['also_block']:
            _block(request.user, target)
        messages.success(request, 'Thank you. Our team will review your report.')
        return redirect('match_list')
    return render(request, 'matches/report.html', {'form': form, 'target': target})