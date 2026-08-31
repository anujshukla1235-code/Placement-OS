from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    """
    STUB — not a working payment flow. This is the one place a real gateway integration
    plugs in. Wire it up like:

        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({...})
        return Response({'order_id': order['id'], 'key_id': settings.RAZORPAY_KEY_ID, ...})

    and have the frontend open Razorpay's checkout widget with that order_id. On success,
    Razorpay calls WebhookView below, which is where you'd create/update the Subscription
    row. Left as a stub because it needs real gateway credentials this environment doesn't
    have — see billing/models.py Subscription docstring for the full checklist.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "error": "Payment gateway not configured. See billing/views.py CheckoutView docstring."
            },
            status=501,
        )


class WebhookView(APIView):
    """
    STUB — payment-gateway webhook receiver. Needs to: verify the gateway's signature
    (never trust an unverified webhook body), then find/create the Subscription for the
    paying user and set status='ACTIVE' + current_period_end from the gateway's payload.
    """

    permission_classes = [
        AllowAny
    ]  # gateways call this unauthenticated; verify by signature instead

    def post(self, request):
        return Response(
            {
                "error": "Payment gateway not configured. See billing/views.py WebhookView docstring."
            },
            status=501,
        )
