from django import forms

from .models import LiveRoom


class LiveRoomForm(forms.ModelForm):
    class Meta:
        model = LiveRoom
        fields = ['title', 'mode', 'is_private']
        labels = {'is_private': 'Private room (not listed, link only)'}