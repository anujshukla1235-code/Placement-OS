from rest_framework import serializers

from accounts.models import CompanyProfile


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            "id",
            "company_name",
            "hr_name",
            "website",
            "gst_number",
            "logo",
            "is_approved",
        ]
