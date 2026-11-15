from django.db.models import Q

from .models import Block


def blocked_user_ids(user):
    """IDs of everyone the user blocked or who blocked the user."""
    pairs = Block.objects.filter(Q(blocker=user) | Q(blocked=user)).values_list('blocker_id', 'blocked_id')
    ids = set()
    for a, b in pairs:
        ids.add(a)
        ids.add(b)
    ids.discard(user.id)
    return ids
