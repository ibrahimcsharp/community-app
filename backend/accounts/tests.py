"""
Tests for register / login / profile.   Run with:  python manage.py test
(They use a temporary test database, your real data is not touched.)
"""
from rest_framework.test import APITestCase

from .models import User


class AccountTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("boss", "boss@test.com", "Admin@123")

    def login(self, username, password):
        return self.client.post("/api/auth/login/", {"username": username, "password": password},
                                format="json")

    def test_register_creates_pending_user(self):
        response = self.client.post("/api/auth/register/", {
            "username": "newbie", "email": "new@test.com", "password": "Secret@123",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.get(username="newbie").status, "pending")

    def test_register_rejects_weak_password(self):
        response = self.client.post("/api/auth/register/", {
            "username": "weak", "email": "weak@test.com", "password": "123",
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_pending_user_cannot_log_in(self):
        User.objects.create_user("waiting", "w@test.com", "Secret@123")  # pending by default
        response = self.login("waiting", "Secret@123")
        self.assertEqual(response.status_code, 403)
        self.assertIn("waiting for admin approval", response.data["detail"])

    def test_wrong_password(self):
        self.assertEqual(self.login("boss", "nope").status_code, 401)

    def test_approved_user_gets_tokens(self):
        response = self.login("boss", "Admin@123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["role"], "admin")

    def test_blocked_user_token_stops_working(self):
        user = User.objects.create_user("bob", "bob@test.com", "Secret@123", status="approved")
        token = self.login("bob", "Secret@123").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

        user.status = "blocked"
        user.save()
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_update_profile(self):
        self.client.force_authenticate(self.admin)
        response = self.client.put("/api/auth/me/", {"bio": "Hello"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["bio"], "Hello")
