from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'gender', 'looking_for', 'city', 'created_at')
    search_fields = ('display_name', 'user__username', 'city')