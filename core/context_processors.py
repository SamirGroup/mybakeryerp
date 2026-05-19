def user_roles(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    is_superadmin = user.is_superuser
    groups = set(user.groups.values_list('name', flat=True))

    # Filial rahbari ma'lumotlari
    user_branch = None
    is_branch_manager = False
    if not is_superadmin and 'branch_admin' in groups:
        try:
            user_branch = user.profile.branch
            is_branch_manager = True
        except Exception:
            pass

    is_accountant_only = (not is_superadmin) and ('accountant' in groups) and len(groups) == 1

    # Filial rahbari uchun to'liq ruxsatlar (superadmin emas, faqat o'z filiali uchun)
    is_branch_admin = is_superadmin or 'branch_admin' in groups

    return {
        'is_superadmin':      is_superadmin,
        'is_accountant':      is_superadmin or 'accountant' in groups or is_branch_manager,
        'is_accountant_only': is_accountant_only,
        'is_hr':              is_superadmin or 'hr' in groups or is_branch_manager,
        'is_seller':          is_superadmin or 'seller' in groups or is_branch_manager,
        'is_branch_admin':    is_branch_admin,
        'is_branch_manager':  is_branch_manager,        # faqat haqiqiy filial rahbari (superadmin emas)
        'is_production_mgr':  is_superadmin or 'production_manager' in groups or is_branch_manager,
        'user_branch':        user_branch,
    }


def menu_context(request):
    """Menu uchun qo'shimcha kontekst"""
    return {
        'menu_items': [
            {
                'title': "Sotuv Bo'limi",
                'icon': 'fa-cash-register',
                'url': '/sales/',
                'visible_for': ['seller', 'superadmin', 'branch_admin'],
                'subitems': [
                    {'title': 'Sotuv Dashboard', 'url': '/sales/', 'icon': 'fa-cash-register'},
                    {'title': 'Mijoz Ekran', 'url': '/sales/customer-display/', 'icon': 'fa-desktop'},
                ]
            },
            {
                'title': 'Ishlab Chiqarish',
                'icon': 'fa-industry',
                'url': '/production/',
                'visible_for': ['production_manager', 'superadmin', 'seller', 'branch_admin'],
                'subitems': [
                    {'title': 'Dashboard', 'url': '/production/', 'icon': 'fa-industry'},
                    {'title': 'Mahsulotlar', 'url': '/production/manage/', 'icon': 'fa-box-open'},
                    {'title': 'Kategoriyalar', 'url': '/production/manage/?tab=tab-categories', 'icon': 'fa-folder'},
                    {'title': 'Retseptlar', 'url': '/production/manage/?tab=tab-recipes', 'icon': 'fa-book-open'},
                    {'title': 'Omborxona', 'url': '/production/manage/?tab=tab-inventory', 'icon': 'fa-warehouse'},
                ]
            },
            {
                'title': 'Buxgalteriya',
                'icon': 'fa-calculator',
                'url': '/accounting/',
                'visible_for': ['accountant', 'superadmin', 'branch_admin'],
                'subitems': [
                    {'title': 'Dashboard', 'url': '/accounting/', 'icon': 'fa-calculator'},
                    {'title': 'Transaktsiyalar', 'url': '/accounting/?tab=transactions', 'icon': 'fa-money-bill-transfer'},
                    {'title': 'Naqd pullar', 'url': '/accounting/?tab=cash-registers', 'icon': 'fa-cash-register'},
                    {'title': 'Yetkazib beruvchilar', 'url': '/accounting/?tab=suppliers', 'icon': 'fa-truck'},
                ]
            },
            {
                'title': "HR Bo'limi",
                'icon': 'fa-users',
                'url': '/hr/',
                'visible_for': ['hr', 'superadmin', 'branch_admin'],
                'subitems': [
                    {'title': 'Dashboard', 'url': '/hr/', 'icon': 'fa-users'},
                    {'title': 'Keldi-Ketdi', 'url': '/hr/?tab=attendance', 'icon': 'fa-clock'},
                    {'title': 'Lavozimlar', 'url': '/hr/?tab=positions', 'icon': 'fa-briefcase'},
                    {'title': 'Face ID', 'url': '/hr/?tab=face-id', 'icon': 'fa-camera'},
                ]
            },
            {
                'title': 'Filiallar',
                'icon': 'fa-store',
                'url': '/branches/',
                'visible_for': ['superadmin'],   # faqat superadmin ko'radi
                'subitems': [
                    {'title': 'Dashboard', 'url': '/branches/', 'icon': 'fa-chart-line'},
                    {'title': 'Filial yaratish', 'url': '/branches/?tab=create', 'icon': 'fa-plus-circle'},
                    {'title': 'Barcha filiallar', 'url': '/branches/?tab=all', 'icon': 'fa-store'},
                ]
            },
        ]
    }
