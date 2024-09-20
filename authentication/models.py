from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from authentication.token_blacklist.token_utils import CustomRefreshToken
from django.db.models import Q
from admin_panel.models import Company, Facility, Zone

# Create your models here.

class CustomRole(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)  # Changed to TextField
    priority = models.IntegerField(default=0)  # Added priority field
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name='user_role', null=True, blank=True)
    email = models.EmailField(verbose_name='email_address', max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(blank=True, max_length=13, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_company', null=True, blank=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='user_facility', null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='user_zone', null=True, blank=True)
    is_staff = models.BooleanField(default=True, db_index=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, max_length=4096)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['email', 'phone_number']),
            models.Index(fields=['is_archive'], condition=Q(is_archive=False), name='unarchive_users_index'),  # Partial index
        ]

    def __str__(self):
        return self.email

    def tokens(self):
        refresh_token, access_token = CustomRefreshToken.for_user(self)
        return {"refresh": str(refresh_token), "access": str(access_token)}

class OTPModel(models.Model):
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    otp = models.CharField(max_length=10)
    expiry_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email