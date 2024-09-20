from rest_framework import routers

from .views import (
    RoleView,
    StateView,
    CityView,
    FacilityView,
    ZoneView,
    UsersView,
    CompanyView,
    CompanyUserView,
    PurposeOfVisitView,
    EmployeesView,
    BulkEmployeeUploadView,
    CompanyVisitorView
)

router = routers.DefaultRouter()

router.register("state", StateView, basename="state")
router.register("city", CityView, basename="city")
router.register("company", CompanyView, basename="company")
router.register("company-user", CompanyUserView, basename="company-user")
router.register("company-visitor", CompanyVisitorView, basename="company-visitor")
router.register("facility", FacilityView, basename="facility")
router.register("zone", ZoneView, basename="zone")
router.register("role", RoleView, basename="role")
router.register("user", UsersView, basename="user")
router.register("employee", EmployeesView, basename="employee")
router.register("purpose-of-visit", PurposeOfVisitView, basename="purpose-of-visit")
router.register("bulk-employee-upload", BulkEmployeeUploadView, basename="bulk-employee-upload")