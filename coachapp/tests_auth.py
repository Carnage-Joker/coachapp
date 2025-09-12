from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class AuthFlowTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="authuser", password="secret123")

    def test_login_refresh_logout_blacklist(self):
        # login
        resp = self.client.post(reverse('token_obtain_pair'), {"username": "authuser", "password": "secret123"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        access = resp.data['access']
        refresh = resp.data['refresh']

        # refresh works
        r2 = self.client.post(reverse('token_refresh'), {"refresh": refresh})
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn('access', r2.data)

        # logout (blacklist)
        r3 = self.client.post(reverse('token_logout'), {"refresh": refresh}, HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(r3.status_code, status.HTTP_205_RESET_CONTENT)

        # refresh should now fail (blacklisted)
        r4 = self.client.post(reverse('token_refresh'), {"refresh": refresh})
        self.assertNotEqual(r4.status_code, status.HTTP_200_OK)

