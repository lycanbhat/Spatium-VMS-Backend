from authentication.urls import router as auth_routes
from admin_panel.urls import router as admin_routes
from vms.urls import router as visitor_routes
from rest_framework import routers

auth_router = routers.SimpleRouter()

# Authentication app urls
auth_router.registry.extend(auth_routes.registry)
auth_router.registry.extend(admin_routes.registry)
auth_router.registry.extend(visitor_routes.registry)