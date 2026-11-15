from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LockoutTests(TestCase):
    def test_lockout_after_five_failures(self):
        User.objects.create_user('lk', password='pass12345!x')
        for _ in range(5):
            self.client.post(reverse('login'), {'username': 'lk', 'password': 'wrong'})
        # Even the correct password must now be refused (axes returns 403 or 429 by version)
        r = self.client.post(reverse('login'), {'username': 'lk', 'password': 'pass12345!x'})
        self.assertIn(r.status_code, (403, 429))
        self.assertNotIn('_auth_user_id', self.client.session)
