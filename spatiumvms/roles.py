from rest_framework_roles.roles import is_user, is_anon, is_admin

def is_front_desk(request, view):
    return is_user(request, view) and request.user.role_id == 3

def is_zone_manager(request, view):
    return is_user(request, view) and request.user.role_id == 1

def is_facility_manager(request, view):
    return is_user(request, view) and request.user.role_id == 2

def is_spoc(request, view):
    return is_user(request, view) and request.user.role_id == 4

ROLES = {
    # Django out-of-the-box
    'admin': is_admin,
    'user': is_user,
    'anon': is_anon,
    'front_desk': is_front_desk,
    'zone_manager': is_zone_manager,
    'facility_manager': is_facility_manager,
    'spoc': is_spoc,
}