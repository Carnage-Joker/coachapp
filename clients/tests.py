from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Client


class ClientOwnershipTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username="alice", password="pass1234")
        self.user2 = User.objects.create_user(username="bob", password="pass1234")
        self.client_api = APIClient()

    def _jwt(self, username: str, password: str) -> str:
        url = reverse('token_obtain_pair')
        res = self.client.post(url, {"username": username, "password": password}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res.data['access']

    def test_anon_cannot_list_clients(self):
        url = reverse('clients-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_creates_client_and_is_owner(self):
        token = self._jwt("alice", "pass1234")
        url = reverse('clients-list')
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "age_group": "25-34",
        }
        res = self.client.post(url, payload, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        obj = Client.objects.get(id=res.data['id'])
        self.assertEqual(obj.user, self.user1)

    def test_user_isolated_visibility(self):
        # Alice creates a client
        token1 = self._jwt("alice", "pass1234")
        url = reverse('clients-list')
        self.client.post(url, {"first_name": "A", "last_name": "A", "age_group": "25-34"}, HTTP_AUTHORIZATION=f"Bearer {token1}")

        # Bob lists and should not see Alice's client
        token2 = self._jwt("bob", "pass1234")
        res = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token2}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

