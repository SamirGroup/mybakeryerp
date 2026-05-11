def user_roles(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    is_superadmin = user.is_superuser
    groups = set(user.groups.values_list('name', flat=True))

    user_branch = None
    if not is_superadmin and 'branch_admin' in groups:
        try:
            user_branch = user.profile.branch
        except Exception:
            pass

    is_accountant_only = (not is_superadmin) and ('accountant' in groups) and len(groups) == 1

    return {
        'is_superadmin':      is_superadmin,
        'is_accountant':      is_superadmin or 'accountant'         in groups,
        'is_accountant_only': is_accountant_only,
        'is_hr':              is_superadmin or 'hr'                 in groups,
        'is_seller':          is_superadmin or 'seller'             in groups,
        'is_branch_admin':    is_superadmin or 'branch_admin'       in groups,
        'is_production_mgr':  is_superadmin or 'production_manager' in groups,
        'user_branch':        user_branch,
    }
