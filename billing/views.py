from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe
from django.conf import settings

from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer


class PlanListView(APIView):
    """Real, working endpoint: lists active plans for the caller's tenant type."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ("COMPANY", "COLLEGE"):
            return Response(
                {"error": "Only company/college accounts have plans"}, status=403
            )
        plans = Plan.objects.filter(
            tenant_type=request.user.role, is_active=True
        ).order_by("price_per_month_inr")
        return Response(PlanSerializer(plans, many=True).data)


class MySubscriptionView(APIView):
    """Real, working endpoint: shows the caller's current plan/status."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sub = request.user.subscription
        except Subscription.DoesNotExist:
            return Response(
                {
                    "subscription": None,
                    "note": "No subscription — billing enforcement is off for this account.",
                }
            )
        return Response(SubscriptionSerializer(sub).data)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {"error": "Stripe is not configured on this server."},
                status=503,
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        plan_id = request.data.get("plan_id")
        success_url = request.data.get("success_url")
        cancel_url = request.data.get("cancel_url")

        if not plan_id:
            return Response({"error": "plan_id is required"}, status=400)
        if not success_url or not cancel_url:
            return Response({"error": "success_url and cancel_url are required"}, status=400)

        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=404)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": plan.name,
                                "description": f"Billing Plan: {plan.name}",
                            },
                            "unit_amount": int(plan.price_per_month_inr * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(request.user.id),
                metadata={
                    "plan_id": str(plan.id),
                    "user_id": str(request.user.id),
                },
            )
            return Response({"checkout_url": session.url})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class WebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
            return Response({"error": "Stripe webhook not configured"}, status=503)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("client_reference_id")
            plan_id = session.get("metadata", {}).get("plan_id")

            if user_id and plan_id:
                try:
                    from accounts.models import User
                    from django.utils import timezone

                    user = User.objects.get(id=user_id)
                    plan = Plan.objects.get(id=plan_id)

                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            "plan": plan,
                            "status": "ACTIVE",
                            "current_period_end": timezone.now() + timezone.timedelta(days=30),
                            "gateway_reference": session.get("id"),
                        },
                    )
                except Exception as e:
                    # Log error in backend
                    pass

        return Response({"status": "success"})
