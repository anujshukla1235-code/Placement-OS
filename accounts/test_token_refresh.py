from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import OTPVerification, User


class TokenRefreshTests(APITestCase):
    """
    Regression test: SIMPLE_JWT has ACCESS_TOKEN_LIFETIME=30min, but /token/refresh/ was
    never wired to any URL — meaning the frontend's silent-refresh flow (lib/api.ts) had
    nowhere to go and every user was force-logged-out every 30 minutes.
    """

    def setUp(self):
        cache.clear()
        user = User.objects.create_user(
            email="refresh1@test.com",
            password="pass1234",
            first_name="T",
            last_name="U",
            role="STUDENT",
            is_active=True,
            is_verified=True,
            consent_student_clause7=True,
        )
        self.client.post(
            "/api/v1/auth/login/",
            {"email": "refresh1@test.com", "password": "pass1234"},
        )
        otp_obj = (
            OTPVerification.objects.filter(user=user, purpose="LOGIN")
            .order_by("-created_at")
            .first()
        )
        mfa_resp = self.client.post(
            "/api/v1/auth/login/verify-mfa/",
            {
                "user_id": str(user.id),
                "otp": otp_obj.otp,
            },
        )
        self.refresh_token = mfa_resp.data["refresh_token"]

    def test_refresh_endpoint_is_reachable(self):
        resp = self.client.post(
            "/api/v1/token/refresh/", {"refresh": self.refresh_token}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)

    def test_refresh_rotates_and_blacklists_old_token(self):
        """With ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION, the old refresh token
        must stop working after use, and a new one is issued."""
        resp1 = self.client.post(
            "/api/v1/token/refresh/", {"refresh": self.refresh_token}
        )
        self.assertEqual(resp1.status_code, 200)
        new_refresh = resp1.data.get("refresh")
        self.assertIsNotNone(new_refresh)
        self.assertNotEqual(new_refresh, self.refresh_token)

        # Old refresh token must now be rejected (blacklisted)
        resp2 = self.client.post(
            "/api/v1/token/refresh/", {"refresh": self.refresh_token}
        )
        self.assertEqual(resp2.status_code, 401)

        # New refresh token must work
        resp3 = self.client.post("/api/v1/token/refresh/", {"refresh": new_refresh})
        self.assertEqual(resp3.status_code, 200)
