def user_has_asset_role(user, *roles):
    if user.is_anonymous:
        return False
    if user.is_superuser or user.is_staff:
        return True
    employee = getattr(user, "employee_profile", None)
    if not employee:
        return False
    current_role = (employee.role or "").strip().lower()
    if not roles:
        return bool(current_role)
    return current_role in {role.lower() for role in roles}


def user_can_manage_assets(user):
    return user_has_asset_role(user, "manager", "technician")
