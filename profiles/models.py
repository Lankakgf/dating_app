from datetime import date

from django.conf import settings
from django.db import models


class Profile(models.Model):
    GENDERS = [('M', 'Man'), ('F', 'Woman'), ('O', 'Other')]
    LOOKING = [('M', 'Men'), ('F', 'Women'), ('A', 'Everyone')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDERS, default='O')
    looking_for = models.CharField(max_length=1, choices=LOOKING, default='A')
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def __str__(self):
        return self.display_name