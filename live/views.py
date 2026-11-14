import time

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from matches.models import Match

from .forms import LiveRoomForm
from .models import LiveRoom

User = get_user_model()


def _adult_ok(user):
    p = getattr(user, 'profile', None)
    return bool(p and p.date_of_birth and p.age() >= 18)


def _name(user):
    p = getattr(user, 'profile', None)
    return p.display_name if p else user.username


def _are_matched(a, b):
    low, high = sorted([a.id, b.id])
    return Match.objects.filter(user1_id=low, user2_id=high).exists()


def _make_token(user, room_name, can_publish):
    now = int(time.time())
    payload = {
        'iss': settings.LIVEKIT_API_KEY,
        'sub': str(user.id),
        'name': _name(user),
        'nbf': now,
        'exp': now + 2 * 60 * 60,
        'video': {
            'room': room_name,
            'roomJoin': True,
            'canPublish': can_publish,
            'canSubscribe': True,
            'canPublishData': can_publish,
        },
    }
    return jwt.encode(payload, settings.LIVEKIT_API_SECRET, algorithm='HS256')


def _token_response(user, room_name, can_publish):
    if not (settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY and settings.LIVEKIT_API_SECRET):
        return JsonResponse({'error': 'Live video is not configured yet.'}, status=503)
    return JsonResponse({
        'token': _make_token(user, room_name, can_publish),
        'url': settings.LIVEKIT_URL,
        'can_publish': can_publish,
    })


@login_required
def lobby(request):
    if not _adult_ok(request.user):
        messages.error(request, 'Complete your profile (18+) to use live video.')
        return redirect('edit_profile')
    rooms = (
        LiveRoom.objects.filter(is_active=True, is_private=False)
        .select_related('host__profile')
        .order_by('-created_at')[:30]
    )
    return render(request, 'live/lobby.html', {'rooms': rooms})


@login_required
def create_room(request):
    if not _adult_ok(request.user):
        return redirect('edit_profile')
    form = LiveRoomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        room = form.save(commit=False)
        room.host = request.user
        room.save()
        return redirect('live_room', slug=room.slug)
    return render(request, 'live/create.html', {'form': form})


@login_required
def room(request, slug):
    if not _adult_ok(request.user):
        return redirect('edit_profile')
    r = get_object_or_404(LiveRoom, slug=slug, is_active=True)
    is_host = r.host_id == request.user.id
    return render(request, 'live/room.html', {
        'title': r.title,
        'subtitle': 'Hosted by ' + _name(r.host),
        'token_url': reverse('live_room_token', args=[slug]),
        'is_host': is_host,
        'end_url': reverse('live_room_end', args=[slug]) if is_host else '',
        'back_url': reverse('live_lobby'),
        'show_invite': True,
        'report_url': '' if is_host else reverse('report_user', args=[r.host_id]),
    })


@login_required
@require_POST
def room_token(request, slug):
    if not _adult_ok(request.user):
        return JsonResponse({'error': 'Complete your profile (18+) first.'}, status=403)
    r = get_object_or_404(LiveRoom, slug=slug, is_active=True)
    can_publish = r.mode == 'group' or r.host_id == request.user.id
    return _token_response(request.user, 'room-' + r.slug, can_publish)


@login_required
@require_POST
def end_room(request, slug):
    r = get_object_or_404(LiveRoom, slug=slug, host=request.user)
    r.is_active = False
    r.save(update_fields=['is_active'])
    messages.success(request, 'Your live room has ended.')
    return redirect('live_lobby')


@login_required
def private_call(request, user_id):
    if not _adult_ok(request.user):
        return redirect('edit_profile')
    other = get_object_or_404(User, pk=user_id)
    if not _are_matched(request.user, other):
        messages.error(request, 'You can only video call people you have matched with.')
        return redirect('match_list')
    return render(request, 'live/room.html', {
        'title': 'Private call',
        'subtitle': 'With ' + _name(other),
        'token_url': reverse('private_call_token', args=[user_id]),
        'is_host': False,
        'end_url': '',
        'back_url': reverse('match_list'),
        'show_invite': False,
        'report_url': reverse('report_user', args=[other.id]),
    })


@login_required
@require_POST
def private_call_token(request, user_id):
    if not _adult_ok(request.user):
        return JsonResponse({'error': 'Complete your profile (18+) first.'}, status=403)
    other = get_object_or_404(User, pk=user_id)
    if not _are_matched(request.user, other):
        return JsonResponse({'error': 'You can only call your matches.'}, status=403)
    low, high = sorted([request.user.id, other.id])
    return _token_response(request.user, 'dm-%d-%d' % (low, high), True)