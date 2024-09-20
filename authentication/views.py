import logging
from .models import  OTPModel
from django.conf import settings
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .serializers import (
    VerifyEmailOTPSerializer,
    CustomTokenRefreshSerializer,
    LogoutSerializer,
    VerifyEmailSerializer
)
from .utils import EmailOTP

logger = logging.getLogger("app")

# Create your views here.


class VerifyEmailView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = VerifyEmailSerializer
    permission_classes = (AllowAny,)
    
    #@method_decorator(ratelimit(key='ip', rate='2/m', method='POST', block=True))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"message": "OTP sent successfully!"}, status=status.HTTP_200_OK
        )

class VerifyEmailOTPView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = VerifyEmailOTPSerializer
    permission_classes = (AllowAny,)

    #@method_decorator(ratelimit(key='ip', rate='2/m', method='POST', block=True))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        OTPModel.objects.filter(email=email).delete()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView, viewsets.GenericViewSet):
    serializer_class = CustomTokenRefreshSerializer

    def create(self, request, *args, **kwargs):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class LogoutView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class MetaDataView(viewsets.GenericViewSet, mixins.ListModelMixin):

    view_permissions = {
        'list': {'admin': True}
    }

    def list(self, request, *args, **kwargs):
        print(request.user)
        return Response(
            {"message": "Hai success"}, status=status.HTTP_200_OK
        )