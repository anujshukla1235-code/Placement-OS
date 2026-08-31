from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from blockchain_module.models import OfferLetter
from jobs.models import Application, Job
from students.models import StudentProfile


class OfferVerificationTamperDetectionTests(APITestCase):
    """
    Regression tests for a critical bug: VerifyOfferView used to have
    `if offer.hash_sha256 == recomputed or True:` — the `or True` made every offer
    verify as valid regardless of whether the stored hash actually matched, which
    defeats the entire purpose of hash-chain tamper detection. Also covers the
    verify endpoint having never been wired to any URL (every QR code 404'd).
    """

    def setUp(self):
        cache.clear()
        company_user = User.objects.create_user(
            email="offerco@test.com",
            password="pass1234",
            first_name="HR",
            last_name="X",
            role="COMPANY",
            is_active=True,
            consent_tenant_clause8=True,
        )
        self.company = CompanyProfile.objects.create(
            user=company_user, company_name="Offer Co", is_approved=True
        )
        self.job = Job.objects.create(
            company=self.company, title="SDE", description="...", ctc="10 LPA"
        )

        student_user = User.objects.create_user(
            email="offerstudent@test.com",
            password="pass1234",
            first_name="Amit",
            last_name="Kumar",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.student = StudentProfile.objects.create(
            user=student_user, enrollment_number="X001", branch="CSE", cgpa=8.0
        )
        self.application = Application.objects.create(
            job=self.job, student=self.student, status="SHORTLISTED"
        )

        self.client.force_authenticate(user=company_user)

    def test_verify_endpoint_is_reachable_at_documented_url(self):
        """Regression: VerifyOfferView existed but was never wired into any urls.py."""
        gen_resp = self.client.post(
            "/api/v1/blockchain/generate/", {"application_id": str(self.application.id)}
        )
        self.assertEqual(gen_resp.status_code, 201, gen_resp.data)
        offer_id = gen_resp.data["offer_id"]

        self.client.force_authenticate(user=None)  # verification is a public endpoint
        verify_resp = self.client.get(f"/verify/offer/{offer_id}/")
        self.assertEqual(verify_resp.status_code, 200)
        self.assertTrue(verify_resp.data["valid"])

    def test_tampered_offer_is_detected_as_invalid(self):
        """Regression: this used to always return valid=True no matter what, because of
        the `or True` bug."""
        gen_resp = self.client.post(
            "/api/v1/blockchain/generate/", {"application_id": str(self.application.id)}
        )
        offer_id = gen_resp.data["offer_id"]

        # Simulate tampering: someone edits the offer content directly in the DB without
        # regenerating the hash.
        offer = OfferLetter.objects.get(id=offer_id)
        offer.content = "TAMPERED: CTC changed to 50 LPA"
        offer.save()

        self.client.force_authenticate(user=None)
        verify_resp = self.client.get(f"/verify/offer/{offer_id}/")
        self.assertEqual(verify_resp.status_code, 200)
        self.assertFalse(verify_resp.data["valid"])
        self.assertIn("tampered", verify_resp.data["reason"].lower())

    def test_untampered_offer_with_joining_date_still_verifies_correctly(self):
        """Regression: joining_date used to be part of the hash but never persisted, so
        recomputing it at verify time with an empty string would falsely flag genuine
        offers as tampered whenever a joining_date had been provided at creation."""
        gen_resp = self.client.post(
            "/api/v1/blockchain/generate/",
            {
                "application_id": str(self.application.id),
                "joining_date": "2026-09-01",
            },
        )
        offer_id = gen_resp.data["offer_id"]

        self.client.force_authenticate(user=None)
        verify_resp = self.client.get(f"/verify/offer/{offer_id}/")
        self.assertTrue(verify_resp.data["valid"])

    def test_verifying_increments_count(self):
        gen_resp = self.client.post(
            "/api/v1/blockchain/generate/", {"application_id": str(self.application.id)}
        )
        offer_id = gen_resp.data["offer_id"]
        self.client.force_authenticate(user=None)
        self.client.get(f"/verify/offer/{offer_id}/")
        self.client.get(f"/verify/offer/{offer_id}/")
        offer = OfferLetter.objects.get(id=offer_id)
        self.assertEqual(offer.verified_count, 2)
