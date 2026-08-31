import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("consent_student_clause7", True)
        extra_fields.setdefault("consent_tenant_clause8", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ("STUDENT", "Student"),
        ("COMPANY", "Company"),
        ("COLLEGE", "College"),
        ("ADMIN", "Admin/TPO"),
    )
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="STUDENT")
    is_verified = models.BooleanField(default=False)
    is_mfa_enabled = models.BooleanField(default=True)
    failed_login_attempts = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    last_device = models.CharField(max_length=255, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    # LEGAL CONSENT - 65 Deliverables Clause 7 & 8
    consent_student_clause7 = models.BooleanField(default=False)
    consent_tenant_clause8 = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class CollegeProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="college_profile"
    )
    college_name = models.CharField(max_length=200)
    tpo_name = models.CharField(max_length=100)
    tpo_phone = models.CharField(max_length=15)
    logo = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.college_name


class CompanyProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="company_profile_new"
    )
    company_name = models.CharField(max_length=200)
    hr_name = models.CharField(max_length=100, blank=True)
    logo = models.URLField(blank=True)
    website = models.URLField(blank=True)
    gst_number = models.CharField(max_length=50, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ("REGISTER", "Registration"),
        ("LOGIN", "Login 2FA"),
        ("FORGOT_PASSWORD", "Forgot Password"),
        ("CHANGE_EMAIL", "Change Email"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (
            not self.is_used and self.attempts < 3 and timezone.now() < self.expires_at
        )


class LoginHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_history"
    )
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
