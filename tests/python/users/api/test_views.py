from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class TestUserRegisterView(APITestCase):
    def test_user_registration(self):
        data = {'first_name': 'Dickson', 'last_name': 'Chibuzor', 'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user = User.objects.first()
        self.assertEqual(new_user.first_name, data['first_name'])


class TestUserView(APITestCase):
    def setUp(self) -> None:
        data = {'first_name': 'Dickson', 'last_name': 'Chibuzor', 'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.new_user = User.objects.get(id=response.json().get('id'))
        self.token = response.json().get('token', '')

    def test_user_login(self):
        data = {'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.new_user.first_name, response.json().get('first_name'))

    def test_user_wrong_details_login(self):
        data = {'email': 'dickson@test.com', 'password': 'wrong password'}

        url = reverse('users_api_v1:login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout_success(self):
        # logout with wrong token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('users_api_v1:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('users_api_v1:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
