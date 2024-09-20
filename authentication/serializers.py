import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from authentication.utils import get_absolute_image_url
from django.contrib import auth
from .utils import EmailOTP, PhoneOTP
from .models import CustomUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from spatiumvms.utils.brevo_utils import send_brevo_email

from spatiumvms.constants import (
    EMAIL_LOGO,
    OTP_VERIFICATION,
    INVALID_EMAIL_FORMAT_ERROR
)

from authentication.token_blacklist.token_utils import (
    CustomAccessToken,
    CustomRefreshToken,
)

logger = logging.getLogger("app")

class VerifyEmailSerializer(serializers.Serializer):

    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)

    def send_email_otp(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError(INVALID_EMAIL_FORMAT_ERROR)
        
        user = CustomUser.objects.filter(email=email, is_archive=False).first()

        if not user:
            raise serializers.ValidationError("Email does not exist.")
        
        otp = EmailOTP.getOTP(email)

        subject = OTP_VERIFICATION.get("subject", "")

        html_body = render_to_string('Otp.html', {'otp': otp, 'logo': EMAIL_LOGO})
        to_emails = [email]
        
        success, message = send_brevo_email(subject, html_body, to_emails)
    
        if success:
            return user
        else:
            raise serializers.ValidationError(message)
    
    def send_phone_number_otp(self, phone_number):
        user = CustomUser.objects.filter(phone_number=phone_number, is_archive=False).first()
        if not user:
            raise serializers.ValidationError("Phone number does not exist.")
        return user
    
    def validate(self, data):
        flag = settings.AUTHENTICATION_FLAG

        if flag == 'email':
            email = data.get('email')
            if not email:
                raise serializers.ValidationError("Email is required.")
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError(INVALID_EMAIL_FORMAT_ERROR)
            
            self.send_email_otp(email)
            
        elif flag == 'phone_number':
            phone_number = data.get('phone_number')
            if not phone_number:
                raise serializers.ValidationError("Phone number is required.")
            
            self.send_phone_number_otp(phone_number)

        return data


class VerifyEmailOTPSerializer(serializers.Serializer):

    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    otp = serializers.CharField(write_only=True, required=False)

    def verify_email(self, email, otp):
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError(INVALID_EMAIL_FORMAT_ERROR)
        
        user = CustomUser.objects.filter(email=email, is_archive=False).first()
        if not user:
            raise serializers.ValidationError("Email does not exist.")
        
        otp_status = EmailOTP.custom_verify_email_otp(email, otp)
        if not otp_status:
            raise serializers.ValidationError("OTP is Incorrect / expired")

        return user

    def verify_phone_number(self, phone_number, otp):
        user = CustomUser.objects.filter(phone_number=phone_number, is_archive=False).first()
        if not user:
            raise serializers.ValidationError("Phone number does not exist.")
        
        otp_status = PhoneOTP.custom_verify_phone_otp(phone_number, otp)
        if not otp_status:
            raise serializers.ValidationError("OTP is Incorrect / expired")

        return user

    def validate(self, data):
        otp = data.get('otp')
        flag = settings.AUTHENTICATION_FLAG

        if flag == 'email':
            email = data.get('email')
            if not email:
                raise serializers.ValidationError("Email is required.")
            
            user = self.verify_email(email, otp)
            
        elif flag == 'phone_number':
            phone_number = data.get('phone_number')
            if not phone_number:
                raise serializers.ValidationError("Phone number is required.")
            
            user = self.verify_phone_number(phone_number, otp)

        user_id = user.id
        role_id = user.role_id
        company_id = user.company_id
        company_name = user.company.name if user.company_id is not None else None
        if user.company_id is not None and user.company.logo:
            company_logo_url = user.company.logo.url
        else:
            company_logo_url = None
        is_superuser = user.is_superuser
        tokens = user.tokens()

        expiry_time = datetime.now() + timedelta(days=settings.TOKEN_EXPIRY_TIME)
        formatted_expiry_time = expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        
        data = {
            'user_id': user_id,
            'email': email,
            'role_id': role_id,
            'company_id': company_id,
            'company_name': company_name,
            'company_logo': company_logo_url,
            'is_superuser': is_superuser,
            'expiry_time': formatted_expiry_time,
            'refresh': str(tokens['refresh']),
            'access': str(tokens['access'])
        }
        
        return data
    
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    access = serializers.CharField(min_length=6, max_length=255, read_only=True)
    refresh = serializers.CharField(min_length=6, max_length=255, required=False)

    error_msg = 'No active account found with the given credentials'

    def validate(self, attrs):
        token_payload = token_backend.decode(attrs['refresh'])
        try:
            user = auth.get_user_model().objects.get(pk=token_payload['user_id'])
            if user.is_active:
                refresh_token = attrs.get("refresh", None)
                new_refresh_token, new_access_token = CustomRefreshToken.refresh_tokens(user, refresh_token)
                
                data = {
                    "access": new_access_token,
                    "refresh" : new_refresh_token
                }

                return data
            else:
                raise AuthenticationFailed(
                    self.error_msg, 'no_active_account'
                )
        except auth.get_user_model().DoesNotExist:
            raise AuthenticationFailed(
                self.error_msg, 'no_active_account'
            )

        except TokenError as error:
            raise AuthenticationFailed(str(error))
        

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    error_msg = 'No active account found with the given credentials'

    def validate(self, attrs):
        request = self.context.get('request', None)
        self.token = attrs.get('refresh')
        self.access_token = str(request.auth)
        token_payload = token_backend.decode(attrs['refresh'])
        try:
            user = auth.get_user_model().objects.get(pk=token_payload['user_id'])
        except auth.get_user_model().DoesNotExist:
            raise AuthenticationFailed(
                self.error_msg, 'no_active_account'
            )
        auth.user_logged_out.send(sender=user.__class__, request=self.context['request'], user=user)
        return attrs
    
    def save(self, **kwargs):
        try:
            CustomRefreshToken(self.token).blacklist()
            CustomAccessToken(self.access_token).blacklist_on_logout()
        except TokenError:
            raise AuthenticationFailed(
                'Token is Expired or Invalid'
            )