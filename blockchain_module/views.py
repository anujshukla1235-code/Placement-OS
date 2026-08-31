import logging

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Application

from .hashing import generate_hash_chain
from .models import OfferLetter
from .qr_generator import generate_qr_code

logger = logging.getLogger("blockchain_module")


class GenerateOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        app_id = request.data.get("application_id")
        app = get_object_or_404(Application, id=app_id)
        if app.job.company.user != request.user and request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)
        content = request.data.get(
            "content",
            f"Offer for {app.student.user.first_name} as {app.job.title} at {app.job.company.company_name} with CTC {app.job.ctc}",
        )
        student_name = f"{app.student.user.first_name} {app.student.user.last_name}"
        company_name = app.job.company.company_name
        role = app.job.title
        ctc = str(app.job.ctc)
        joining_date = request.data.get("joining_date", "")
        # get previous hash
        last = OfferLetter.objects.order_by("-issued_at").first()
        prev_hash = last.hash_sha256 if last else "0" * 64
        hash_val = generate_hash_chain(
            content, prev_hash, student_name, company_name, role, ctc, joining_date
        )
        offer, created = OfferLetter.objects.get_or_create(
            application=app,
            defaults={
                "content": content,
                "joining_date": joining_date,
                "hash_sha256": hash_val,
                "previous_hash": prev_hash,
            },
        )
        if not created:
            offer.content = content
            offer.joining_date = joining_date
            offer.hash_sha256 = hash_val
            offer.previous_hash = prev_hash
            offer.save()
        # QR
        try:
            logger.info(
                "offer_generated",
                extra={
                    "event": "offer_generated",
                    "offer_id": str(offer.id),
                    "application_id": str(app.id),
                    "issuer_id": str(request.user.id),
                },
            )
        except Exception:
            pass
        verify_url = f"{request.build_absolute_uri('/')[:-1]}/verify/offer/{offer.id}/"
        qr_file = generate_qr_code(verify_url, f"qr_{offer.id}.png")
        offer.qr_code.save(f"qr_{offer.id}.png", qr_file, save=True)
        app.status = "OFFERED"
        app.save()
        return Response(
            {
                "offer_id": str(offer.id),
                "hash": hash_val,
                "qr_code_url": offer.qr_code.url if offer.qr_code else "",
                "verify_url": verify_url,
            },
            status=201,
        )


class VerifyOfferView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, offer_id):
        try:
            offer = OfferLetter.objects.select_related(
                "application__student__user", "application__job__company"
            ).get(id=offer_id)
        except OfferLetter.DoesNotExist:
            return Response({"valid": False, "reason": "Offer not found"}, status=404)

        app = offer.application
        student_name = f"{app.student.user.first_name} {app.student.user.last_name}"
        company_name = app.job.company.company_name
        role = app.job.title
        ctc = str(app.job.ctc)
        recomputed = generate_hash_chain(
            offer.content,
            offer.previous_hash,
            student_name,
            company_name,
            role,
            ctc,
            offer.joining_date,
        )

        # Real tamper check: the stored hash must match what we recompute from the
        # offer's own stored fields. A previous version of this endpoint always
        # reported valid=True regardless of this comparison — that defeated the whole
        # point of hash-chain verification, so any tampered/corrupted offer would have
        # silently passed as genuine.
        if offer.hash_sha256 != recomputed:
            return Response({"valid": False, "reason": "Hash mismatch - tampered"})

        offer.verified_count += 1
        offer.save(update_fields=["verified_count"])
        return Response(
            {
                "valid": True,
                "student_name": student_name,
                "company": company_name,
                "role": role,
                "ctc": ctc,
                "issued_at": offer.issued_at,
                "verified_count": offer.verified_count,
            }
        )


class OfferDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id):
        offer = get_object_or_404(OfferLetter, id=offer_id)
        return Response(
            {
                "id": str(offer.id),
                "content": offer.content,
                "hash": offer.hash_sha256,
                "qr_code_url": offer.qr_code.url if offer.qr_code else "",
                "issued_at": offer.issued_at,
            }
        )
