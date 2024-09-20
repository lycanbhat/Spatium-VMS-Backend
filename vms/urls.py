from rest_framework import routers

from .views import (
    VisitorView,
    QRCodeView,
    IdentityCardView,
    VMSDashboardView,
    CompanyVisitorView
)

router = routers.DefaultRouter()


router.register("visitor", VisitorView, basename="visitor")
router.register("qr-code", QRCodeView, basename="qr-code")
router.register("identity-card", IdentityCardView, basename="identity-card")
router.register("vms-dashboard", VMSDashboardView, basename="vms-dashboard")
router.register("company-visitor", CompanyVisitorView, basename="company-visitor")