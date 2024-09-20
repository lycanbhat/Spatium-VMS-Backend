import base64
import logging
import pyotp
from datetime import timedelta
from django.conf import settings
from .models import OTPModel
from django.utils import timezone


logger = logging.getLogger("app")


class GenerateKey:
    @staticmethod
    def returnValue(email):
        return str(email) + str(timezone.now()) + settings.SECRET_KEY

class EmailOTP:
    @staticmethod
    def getOTP(email):
        keygen = GenerateKey()
        key = base64.b32encode(keygen.returnValue(email).encode())
        OTP = pyotp.TOTP(key,interval = settings.OTP_EXPIRY_TIME)

        otp_value = OTP.now()
        expiry_time = timezone.now() + timedelta(minutes=10)
        
        otp_model, created = OTPModel.objects.get_or_create(email=email)
        otp_model.otp = otp_value
        otp_model.expiry_time = expiry_time
        otp_model.save()

        return otp_value

    @staticmethod
    def custom_verify_email_otp(email, otp_code):
        try:
            otp_model = OTPModel.objects.get(email=email)
        except OTPModel.DoesNotExist:
            logger.error(f"exception on otp detail not found for email : {email}")
            return False

        # Check if the stored OTP matches the given OTP and the expiry time is in the future
        current_time = timezone.now()

        if otp_model.otp == otp_code and otp_model.expiry_time is not None and otp_model.expiry_time >= timezone.now():
            logger.info(f"otp detail verified for email : {email}, expired on : {otp_model.expiry_time}, current time: {current_time}")
            return True

        logger.error(f"otp detail not verified for email : {email}, expired on : {otp_model.expiry_time}, current time: {current_time}")
        return False
    
class PhoneOTP:
    @staticmethod
    def getOTP(phone_number):
        keygen = GenerateKey()
        key = base64.b32encode(keygen.returnValue(phone_number).encode())
        OTP = pyotp.TOTP(key,interval = settings.OTP_EXPIRY_TIME)

        otp_value = OTP.now()
        expiry_time = timezone.now() + timedelta(minutes=10)
        
        otp_model, created = OTPModel.objects.get_or_create(phone_number=phone_number)
        otp_model.otp = otp_value
        otp_model.expiry_time = expiry_time
        otp_model.save()

        return otp_value

    @staticmethod
    def custom_verify_phone_otp(phone_number, otp_code):
        try:
            otp_model = OTPModel.objects.get(phone_number=phone_number)
        except OTPModel.DoesNotExist:
            logger.error(f"exception on otp detail not found for phone_number : {phone_number}")
            return False

        # Check if the stored OTP matches the given OTP and the expiry time is in the future
        current_time = timezone.now()

        if otp_model.otp == otp_code and otp_model.expiry_time is not None and otp_model.expiry_time >= timezone.now():
            logger.info(f"otp detail verified for phone_number : {phone_number}, expired on : {otp_model.expiry_time}, current time: {current_time}")
            return True

        logger.error(f"otp detail not verified for phone_number : {phone_number}, expired on : {otp_model.expiry_time}, current time: {current_time}")
        return False

def get_absolute_image_url(request, instance):
    result_image = instance.url
    return request.build_absolute_uri(result_image)