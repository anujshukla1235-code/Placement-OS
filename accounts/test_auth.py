from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import OTPVerification, User


class ThrottleSafeAPITestCase(APITestCase):
    """
    Registration/login throttle scopes are intentionally strict in production
    (5/hour for register, 10/min for login) to stop abuse. DRF binds throttle rates
    to the throttle class at import time, so `override_settings` can't change them
    at test-time — clearing the request cache before each test is what actually
    resets the throttle counters, so tests exercise application logic rather than
    tripping the rate limiter meant for real abusive traffic.
    """

    def setUp(self):
        cache.clear()
        super().setUp()


class RegistrationTests(ThrottleSafeAPITestCase):
    """Covers the bug this session fixed: role case, missing consent, org_name handling."""

    def test_student_register_requires_clause7_consent(self):
        resp = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Test",
                "last_name": "Student",
                "email": "s1@test.com",
                "password": "pass1234",
                "role": "STUDENT",
            },
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("consent_student_clause7", resp.data)

    def test_student_register_succeeds_with_consent(self):
        resp = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Test",
                "last_name": "Student",
                "email": "s2@test.com",
                "password": "pass1234",
                "role": "STUDENT",
                "consent_student_clause7": True,
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertIn("user_id", resp.data)

    def test_company_register_requires_org_name(self):
        resp = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Test",
                "last_name": "HR",
                "email": "c1@test.com",
                "password": "pass1234",
                "role": "COMPANY",
                "consent_tenant_clause8": True,
            },
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("org_name", resp.data)

    def test_company_register_saves_real_org_name(self):
        """Regression test: signup used to save '<firstname> Company' as a placeholder
        instead of the name the user actually typed."""
        resp = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Neha",
                "last_name": "Verma",
                "email": "c2@test.com",
                "password": "pass1234",
                "role": "COMPANY",
                "consent_tenant_clause8": True,
                "org_name": "Zenith Technologies Pvt Ltd",
            },
        )
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(email="c2@test.com")
        self.assertEqual(
            user.company_profile_new.company_name, "Zenith Technologies Pvt Ltd"
        )

    def test_lowercase_role_is_rejected(self):
        """Regression test: frontend used to send lowercase 'student', which the backend
        ROLE_CHOICES (uppercase) would silently reject."""
        resp = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Test",
                "last_name": "Student",
                "email": "s3@test.com",
                "password": "pass1234",
                "role": "student",
                "consent_student_clause7": True,
            },
        )
        self.assertEqual(resp.status_code, 400)


class LoginMFATests(ThrottleSafeAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Test",
                "last_name": "Student",
                "email": "login1@test.com",
                "password": "pass1234",
                "role": "STUDENT",
                "consent_student_clause7": True,
            },
        )
        user = User.objects.get(email="login1@test.com")
        user.is_active = True
        user.is_verified = True
        user.save()
        self.user = user

    def test_login_requires_mfa_otp(self):
        resp = self.client.post(
            "/api/v1/auth/login/", {"email": "login1@test.com", "password": "pass1234"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get("mfa_required"))
        self.assertIn("user_id", resp.data)
        # no access token yet — MFA step hasn't been completed
        self.assertNotIn("access_token", resp.data)

    def test_full_login_flow_with_correct_otp_returns_tokens(self):
        self.client.post(
            "/api/v1/auth/login/", {"email": "login1@test.com", "password": "pass1234"}
        )
        otp_obj = (
            OTPVerification.objects.filter(user=self.user, purpose="LOGIN")
            .order_by("-created_at")
            .first()
        )
        resp = self.client.post(
            "/api/v1/auth/login/verify-mfa/",
            {
                "user_id": str(self.user.id),
                "otp": otp_obj.otp,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.data)

    def test_wrong_password_returns_401_not_500(self):
        resp = self.client.post(
            "/api/v1/auth/login/", {"email": "login1@test.com", "password": "wrongpass"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_wrong_otp_is_rejected(self):
        self.client.post(
            "/api/v1/auth/login/", {"email": "login1@test.com", "password": "pass1234"}
        )
        resp = self.client.post(
            "/api/v1/auth/login/verify-mfa/",
            {
                "user_id": str(self.user.id),
                "otp": "000000",
            },
        )
        self.assertEqual(resp.status_code, 400)


class AccountDeletionTests(ThrottleSafeAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Del",
                "last_name": "Me",
                "email": "del1@test.com",
                "password": "pass1234",
                "role": "STUDENT",
                "consent_student_clause7": True,
            },
        )
        self.user = User.objects.get(email="del1@test.com")
        self.user.is_active = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_delete_requires_correct_password(self):
        resp = self.client.post("/api/v1/auth/me/delete/", {"password": "wrongpass"})
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(User.objects.filter(email="del1@test.com").exists())

    def test_delete_removes_account(self):
        resp = self.client.post("/api/v1/auth/me/delete/", {"password": "pass1234"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email="del1@test.com").exists())
