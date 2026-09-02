from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123!",
        )
        self.login_url = "/api/accounts/login/"

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "WrongPassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )