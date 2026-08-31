from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CompanyProfile

from .serializers import CompanySerializer


class CompanyMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            c = CompanyProfile.objects.get(user=request.user)
            return Response(
                {
                    "company_name": c.company_name,
                    "hr_name": c.hr_name,
                    "website": c.website,
                    "gstin": c.gst_number,
                    "logo": c.logo,
                    "is_approved": c.is_approved,
                }
            )
        except CompanyProfile.DoesNotExist:
            return Response({"error": "Not a company"}, status=404)

    def put(self, request):
        c, _ = CompanyProfile.objects.get_or_create(
            user=request.user,
            defaults={"company_name": request.data.get("company_name", "")},
        )
        if "company_name" in request.data:
            c.company_name = request.data["company_name"]
        if "hr_name" in request.data:
            c.hr_name = request.data["hr_name"]
        if "website" in request.data:
            c.website = request.data["website"]
        if "gstin" in request.data:
            c.gst_number = request.data["gstin"]
        if "logo" in request.data:
            c.logo = request.data["logo"]
        c.save()
        return Response({"message": "Updated"})


# NOTE: company/college approval (with email notification) is handled by the more
# complete accounts.admin_views.PendingApprovalsAPIView / ApproveRejectAPIView
# (/api/v1/auth/approvals/) which covers both tenant types and sends a real email.
# A separate, weaker company-only approval endpoint used to live here — removed to
# avoid two competing approval flows.


class CompanyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    queryset = CompanyProfile.objects.filter(is_approved=True).all()

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q") or self.request.GET.get("search")
        if q:
            try:
                from django.contrib.postgres.search import (
                    SearchQuery,
                    SearchRank,
                    SearchVector,
                )

                vector = SearchVector("company_name", weight="A") + SearchVector(
                    "website", weight="B"
                )
                query = SearchQuery(q)
                qs = (
                    qs.annotate(rank=SearchRank(vector, query))
                    .filter(rank__gte=0.1)
                    .order_by("-rank")
                )
            except Exception:
                qs = qs.filter(
                    models.Q(company_name__icontains=q) | models.Q(website__icontains=q)
                )
        return qs.order_by("-company_name")
