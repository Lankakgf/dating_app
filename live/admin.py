from django.contrib import admin

from .models import LiveRoom


@admin.register(LiveRoom)
class LiveRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'mode', 'is_private', 'is_active', 'created_at')
    list_filter = ('mode', 'is_private', 'is_active')