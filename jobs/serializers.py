from rest_framework import serializers

from .models import Application, Job


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_name", read_only=True)

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ["id", "company", "created_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(
        source="job.company.company_name", read_only=True
    )
    student_name = serializers.CharField(
        source="student.user.first_name", read_only=True
    )

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["id", "applied_at", "updated_at"]
