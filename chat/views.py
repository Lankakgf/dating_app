from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from matches.models import Match

from .models import Message

User = get_user_model()


def _other_if_matched(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    low, high = sorted([request.user.id, other.id])
    ok = Match.objects.filter(user1_id=low, user2_id=high).exists()
    return other, ok


def _thread(a, b):
    return Message.objects.filter(Q(sender=a, recipient=b) | Q(sender=b, recipient=a))


@login_required
def thread(request, user_id):
    other, ok = _other_if_matched(request, user_id)
    if not ok:
        messages.error(request, 'You can only chat with your matches.')
        return redirect('match_list')
    msgs = list(_thread(request.user, other).order_by('-id')[:100])[::-1]
    return render(request, 'chat/thread.html', {
        'other': other,
        'chat_messages': msgs,
        'last_id': msgs[-1].id if msgs else 0,
    })


@login_required
@require_POST
def send(request, user_id):
    other, ok = _other_if_matched(request, user_id)
    if not ok:
        return JsonResponse({'error': 'not allowed'}, status=403)
    text = (request.POST.get('text') or '').strip()[:1000]
    if text:
        Message.objects.create(sender=request.user, recipient=other, text=text)
    return JsonResponse({'ok': True})


@login_required
def poll(request, user_id):
    other, ok = _other_if_matched(request, user_id)
    if not ok:
        return JsonResponse({'error': 'not allowed'}, status=403)
    try:
        after = int(request.GET.get('after') or 0)
    except ValueError:
        after = 0
    qs = _thread(request.user, other).filter(id__gt=after).order_by('id')
    data = [
        {
            'id': m.id,
            'mine': m.sender_id == request.user.id,
            'text': m.text,
            'time': timezone.localtime(m.created_at).strftime('%H:%M'),
        }
        for m in qs
    ]
    return JsonResponse({'messages': data})