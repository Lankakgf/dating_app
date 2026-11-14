import secrets

from django.conf import settings
from django.db import models


def make_slug():
    return secrets.token_urlsafe(8)


class LiveRoom(models.Model):
    MODES = [
        ('broadcast', 'Broadcast: I stream, others watch'),
        ('group', 'Group video: everyone can join on camera'),
    ]

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_rooms')
    title = models.CharField(max_length=80)
    mode = models.CharField(max_length=10, choices=MODES, default='broadcast')
    is_private = models.BooleanField(
        default=False, help_text='Private rooms are not listed. Only people with your link can join.'
    )
    slug = models.CharField(max_length=20, unique=True, default=make_slug, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title