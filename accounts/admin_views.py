from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CollegeProfile, CompanyProfile, User


class PendingApprovalsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pending_companies = CompanyProfile.objects.filter(
            is_approved=False
        ).select_related("user")
        pending_colleges = CollegeProfile.objects.filter(
            is_approved=False
        ).select_related("user")

        results = []
        for p in pending_companies:
            results.append(
                {
                    "profile_id": str(p.id),
                    "user_id": str(p.user.id),
                    "role": "COMPANY",
                    "company_name": p.company_name,
                    "website": p.website,
                    "logo": p.logo,
                    "email": p.user.email,
                }
            )
        for p in pending_colleges:
            results.append(
                {
                    "profile_id": str(p.id),
                    "user_id": str(p.user.id),
                    "role": "COLLEGE",
                    "college_name": p.college_name,
                    "tpo_name": p.tpo_name,
                    "tpo_phone": p.tpo_phone,
                    "logo": p.logo,
                    "email": p.user.email,
                }
            )
        return Response(results)


class ApproveRejectAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        action = request.data.get("action")
        reason = request.data.get("reason", "")

        if action not in ["approve", "reject"]:
            return Response(
                {"error": "action must be approve or reject"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Handle company profile
        profile_updated = False
        if hasattr(user, "company_profile_new"):
            profile = user.company_profile_new
            if action == "approve":
                profile.is_approved = True
                user.is_active = True
            else:
                profile.is_approved = False
                user.is_active = False
            profile.save()
            profile_updated = True

        # Handle college profile
        if hasattr(user, "college_profile"):
            profile = user.college_profile
            if action == "approve":
                profile.is_approved = True
                user.is_active = True
            else:
                profile.is_approved = False
                user.is_active = False
            profile.save()
            profile_updated = True

        if not profile_updated:
            return Response(
                {"error": "No company/college profile associated with user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.save()

        # Send notification email via Brevo (fallback to Django send_mail)
        subject = "Account Approval Update"
        if action == "approve":
            subject = "Your account has been approved"
            message = f"Hello {user.first_name},\n\nYour account has been approved by the admin. You can now access the full dashboard.\n\n- Team"
        else:
            subject = "Your account has been rejected"
            message = f"Hello {user.first_name},\n\nYour account registration was rejected by the admin. Reason: {reason}\nIf you believe this is an error, please contact support.\n\n- Team"

        try:
            if getattr(settings, "BREVO_API_KEY", ""):
                try:
                    import sib_api_v3_sdk

                    configuration = sib_api_v3_sdk.Configuration()
                    configuration.api_key["api-key"] = settings.BREVO_API_KEY
                    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                        sib_api_v3_sdk.ApiClient(configuration)
                    )
                    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                        to=[{"email": user.email, "name": user.first_name}],
                        sender={
                            "email": getattr(
                                settings,
                                "DEFAULT_FROM_EMAIL",
                                "noreply@shukl-placement.com",
                            ),
                            "name": "Shukl Placement",
                        },
                        subject=subject,
                        text_content=message,
                    )
                    api_instance.send_transac_email(send_smtp_email)
                except Exception:
                    # Fall back to Django email if Brevo SDK isn't available or call fails
                    send_mail(
                        subject,
                        message,
                        getattr(
                            settings,
                            "DEFAULT_FROM_EMAIL",
                            "noreply@shukl-placement.com",
                        ),
                        [user.email],
                        fail_silently=False,
                    )
            else:
                send_mail(
                    subject,
                    message,
                    getattr(
                        settings, "DEFAULT_FROM_EMAIL", "noreply@shukl-placement.com"
                    ),
                    [user.email],
                    fail_silently=False,
                )
        except Exception:
            try:
                send_mail(
                    subject,
                    message,
                    getattr(
                        settings, "DEFAULT_FROM_EMAIL", "noreply@shukl-placement.com"
                    ),
                    [user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        return Response({"status": "ok", "action": action})
