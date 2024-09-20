from rest_framework import routers

from .views import (
    CustomTokenRefreshView,
    VerifyEmailOTPView,
    VerifyEmailView,
    LogoutView,
    MetaDataView
)

router = routers.DefaultRouter()


router.register("verify-email", VerifyEmailView, basename="verify-email")
router.register("verify-otp", VerifyEmailOTPView, basename="verify-otp")
router.register('token/refresh', CustomTokenRefreshView, basename='refresh-token')
router.register('logout', LogoutView, basename='logout')
router.register("meta-data", MetaDataView, basename="meta-data")