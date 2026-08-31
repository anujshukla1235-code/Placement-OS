from rest_framework import serializers

from .models import CollegeProfile, CompanyProfile, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=["STUDENT", "COMPANY", "COLLEGE"], default="STUDENT"
    )
    # Legal consent - 65 deliverables
    consent_student_clause7 = serializers.BooleanField(required=False, default=False)
    consent_tenant_clause8 = serializers.BooleanField(required=False, default=False)
    # Organisation name, required for COMPANY/COLLEGE signup (ignored for STUDENT)
    org_name = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "mobile",
            "password",
            "role",
            "consent_student_clause7",
            "consent_tenant_clause8",
            "org_name",
        ]

    def validate(self, data):
        role = data.get("role")
        if role == "STUDENT" and not data.get("consent_student_clause7"):
            raise serializers.ValidationError(
                {
                    "consent_student_clause7": "Student must agree to Clause 7 - Privacy Policy"
                }
            )
        if role in ["COMPANY", "COLLEGE"] and not data.get("consent_tenant_clause8"):
            raise serializers.ValidationError(
                {
                    "consent_tenant_clause8": "Tenant must agree to Clause 8 - Tenant Agreement"
                }
            )
        if role in ["COMPANY", "COLLEGE"] and not data.get("org_name"):
            raise serializers.ValidationError(
                {"org_name": f"{role.title()} name is required"}
            )
        return data

    def create(self, validated_data):
        # Extract consent + org name (not User model fields)
        c7 = validated_data.pop("consent_student_clause7", False)
        c8 = validated_data.pop("consent_tenant_clause8", False)
        org_name = validated_data.pop("org_name", "")
        user = User.objects.create_user(
            **validated_data, consent_student_clause7=c7, consent_tenant_clause8=c8
        )
        if validated_data.get("role") in ["COMPANY", "COLLEGE"]:
            user.is_active = False
        user.save()
        # Create profiles using the actual organisation name provided at signup
        if validated_data.get("role") == "COLLEGE":
            CollegeProfile.objects.create(
                user=user,
                college_name=org_name,
                tpo_name=f"{validated_data.get('first_name', '')} {validated_data.get('last_name', '')}".strip(),
                tpo_phone=validated_data.get("mobile", ""),
            )
        if validated_data.get("role") == "COMPANY":
            CompanyProfile.objects.create(user=user, company_name=org_name)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
