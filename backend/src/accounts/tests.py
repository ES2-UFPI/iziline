from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_creates_and_authenticates(self):
        r = self.client.post(
            reverse("auth-register"),
            {"username": "ana", "password": "Iziline#2026", "first_name": "Ana", "last_name": "Silva"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["username"], "ana")
        self.assertEqual(r.data["name"], "Ana Silva")
        self.assertTrue(User.objects.filter(username="ana").exists())
        me = self.client.get(reverse("auth-me"))
        self.assertEqual(me.data["username"], "ana")

    def test_register_duplicate_username(self):
        User.objects.create_user(username="ana", password="x")
        r = self.client.post(
            reverse("auth-register"), {"username": "ana", "password": "Iziline#2026"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_register_rejects_weak_password(self):
        r = self.client.post(
            reverse("auth-register"), {"username": "novo", "password": "123456"}, format="json"
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("password", r.data)
        self.assertFalse(User.objects.filter(username="novo").exists())

    def test_login_valid(self):
        User.objects.create_user(username="ana", password="secret123")
        r = self.client.post(
            reverse("auth-login"), {"username": "ana", "password": "secret123"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "ana")

    def test_login_invalid(self):
        User.objects.create_user(username="ana", password="secret123")
        r = self.client.post(
            reverse("auth-login"), {"username": "ana", "password": "errada"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_me_anonymous_returns_null(self):
        r = self.client.get(reverse("auth-me"))
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data)

    def test_logout(self):
        User.objects.create_user(username="ana", password="secret123")
        self.client.login(username="ana", password="secret123")
        r = self.client.post(reverse("auth-logout"))
        self.assertEqual(r.status_code, 204)
        self.assertIsNone(self.client.get(reverse("auth-me")).data)
