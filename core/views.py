from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from sales.models import Sale
from production.models import ProductionLog
from accounting.models import CashRegister, Supplier
from hr.models import Employee
from accounting.models import Transaction
from sales.models import SaleItem
from branches.models import BranchSale, BranchSaleItem, Branch
from .models import UserProfile


ROLE_GROUPS = ['accountant', 'hr', 'seller', 'branch_admin', 'production_manager']


def _ensure_groups():
    for name in ROLE_GROUPS:
        Group.objects.get_or_create(name=name)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect(request.POST.get('next') or 'dashboard')
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(data=request.POST)
        form.is_valid()
        return render(request, 'login.html', {'form': form})
    from django.contrib.auth.forms import AuthenticationForm
    return render(request, 'login.html', {'form': AuthenticationForm()})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def branch_dashboard(request):
    """Filial rahbari uchun alohida dashboard — faqat o'z filiali"""
    user = request.user
    if user.is_superuser:
        return redirect('dashboard')
    if 'branch_admin' not in user.groups.values_list('name', flat=True):
        return redirect('dashboard')

    try:
        user_branch = user.profile.branch
    except Exception:
        messages.error(request, "Sizga filial biriktirilmagan.")
        return redirect('login')
    
    if not user_branch:
        messages.error(request, "Sizga filial biriktirilmagan.")
        return redirect('login')
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Filial bo'yicha sotuvlar
    from sales.models import Sale, SaleItem
    from branches.models import BranchSale, BranchSaleItem
    from production.models import ProductionLog
    from accounting.models import Transaction, CashRegister
    from hr.models import Employee, DailyReport
    
    # Bugungi sotuvlar (POS + filial)
    today_pos_sales = Sale.objects.filter(date__date=today, seller__profile__branch=user_branch)
    today_branch_sales = BranchSale.objects.filter(date=today, branch=user_branch)
    
    today_revenue = (today_pos_sales.aggregate(total=Sum('total_amount'))['total'] or 0) + \
                    (today_branch_sales.aggregate(total=Sum('total_amount'))['total'] or 0)
    
    yesterday_pos_sales = Sale.objects.filter(date__date=yesterday, seller__profile__branch=user_branch)
    yesterday_branch_sales = BranchSale.objects.filter(date=yesterday, branch=user_branch)
    yesterday_revenue = (yesterday_pos_sales.aggregate(total=Sum('total_amount'))['total'] or 0) + \
                        (yesterday_branch_sales.aggregate(total=Sum('total_amount'))['total'] or 0)
    
    revenue_delta = today_revenue - yesterday_revenue
    
    # Ishlab chiqarish (filial bo'yicha xodimlar orqali)
    branch_employees = Employee.objects.filter(branch=user_branch)
    employee_ids = list(branch_employees.values_list('id', flat=True))
    
    today_production = ProductionLog.objects.filter(
        date__date=today,
        baker_name__in=branch_employees.values_list('name', flat=True)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Xodimlar statistikasi
    total_employees = branch_employees.count()
    active_employees = branch_employees.filter(status='active').count()
    
    # Bugungi davomat
    today_reports = DailyReport.objects.filter(date=today, employee__branch=user_branch)
    present_today = today_reports.filter(was_present=True).count()
    late_today = today_reports.filter(check_in__gt='09:00').count()  # sodda kechikish
    
    # Top mahsulotlar
    top_products = SaleItem.objects.filter(
        sale__date__date=today,
        sale__seller__profile__branch=user_branch
    ).values('product__name').annotate(total=Sum('quantity')).order_by('-total')[:5]
    
    context = {
        'branch': user_branch,
        'today_revenue': today_revenue,
        'yesterday_revenue': yesterday_revenue,
        'revenue_delta': revenue_delta,
        'today_production': today_production,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'present_today': present_today,
        'late_today': late_today,
        'top_products': top_products,
        'today': today,
    }
    return render(request, 'branch_dashboard.html', context)


@login_required
def admin_users(request):
    # Superadmin yoki branch_admin kirishi mumkin
    is_super = request.user.is_superuser
    is_branch_mgr = (not is_super) and request.user.groups.filter(name='branch_admin').exists()
    if not is_super and not is_branch_mgr:
        return redirect('dashboard')

    _ensure_groups()

    # Branch admin faqat o'z filialini ko'radi
    if is_branch_mgr:
        try:
            my_branch = request.user.profile.branch
        except Exception:
            messages.error(request, "Filial biriktirilmagan.")
            return redirect('dashboard')
        branches = Branch.objects.filter(id=my_branch.id)
    else:
        branches = Branch.objects.all()
        my_branch = None
    # Branch_admin ruxsat etilgan rollar (superadmin va branch_admin yarata olmaydi)
    BRANCH_ALLOWED_ROLES = ['hr', 'seller', 'accountant', 'production_manager']

    if request.method == 'POST':
        if request.POST.get('delete_user_id'):
            uid = request.POST.get('delete_user_id')
            try:
                u = User.objects.get(id=uid)
                if u != request.user:
                    # Branch admin faqat o'z filial foydalanuvchilarini o'chirishi mumkin
                    if is_branch_mgr:
                        try:
                            if u.profile.branch != my_branch:
                                messages.error(request, "Siz faqat o'z filial foydalanuvchilarini o'chira olasiz.")
                                return redirect('admin_users')
                        except Exception:
                            pass
                    u.delete()
                    messages.success(request, "Foydalanuvchi o'chirildi.")
            except User.DoesNotExist:
                pass
        elif request.POST.get('action') == 'create_branch_with_admin' and is_super:
            bname = request.POST.get('branch_name', '').strip()
            baddr = request.POST.get('branch_address', '').strip()
            resp = request.POST.get('responsible_person', '').strip()
            username = request.POST.get('ba_username', '').strip()
            password = request.POST.get('ba_password', '').strip()
            if not bname or not username or not password:
                messages.error(request, "Filial nomi, login va parol majburiy.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Bu login band — boshqa nom tanlang.")
            else:
                try:
                    with transaction.atomic():
                        branch = Branch.objects.create(
                            name=bname,
                            address=baddr,
                            responsible_person=resp,
                        )
                        u = User.objects.create_user(username=username, password=password)
                        group, _ = Group.objects.get_or_create(name='branch_admin')
                        u.groups.add(group)
                        UserProfile.objects.create(
                            user=u,
                            branch=branch,
                            first_name=request.POST.get('ba_first_name', '').strip(),
                            last_name=request.POST.get('ba_last_name', '').strip(),
                            phone=request.POST.get('ba_phone', '').strip(),
                            address=baddr,
                        )
                    messages.success(
                        request,
                        f"Filial «{bname}» yaratildi. Filial kirishi: login «{username}».",
                    )
                except Exception as e:
                    messages.error(request, str(e) or "Yaratishda xato.")
        else:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            role = request.POST.get('role', 'seller')
            branch_id = request.POST.get('branch_id', '')

            # Branch admin faqat ruxsat etilgan rollarni yarata oladi
            if is_branch_mgr and role not in BRANCH_ALLOWED_ROLES:
                messages.error(request, f"Filial admin faqat {', '.join(BRANCH_ALLOWED_ROLES)} yarata oladi.")
                return redirect('admin_users')

            if username and password:
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Bu login allaqachon mavjud.")
                else:
                    make_super = (role == 'superadmin') and is_super
                    u = User.objects.create_user(
                        username=username,
                        password=password,
                        is_superuser=make_super,
                        is_staff=make_super,
                    )
                    if not make_super:
                        group, _ = Group.objects.get_or_create(name=role)
                        u.groups.add(group)
                    profile = UserProfile.objects.create(user=u)

                    # Filial biriktirish
                    if is_branch_mgr:
                        # Branch admin yaratgan foydalanuvchi avtomatik o'z filialiga biriktiriladi
                        profile.branch = my_branch
                    elif role == 'branch_admin' and branch_id:
                        try:
                            profile.branch = Branch.objects.get(id=branch_id)
                        except Branch.DoesNotExist:
                            pass
                    elif branch_id:
                        try:
                            profile.branch = Branch.objects.get(id=branch_id)
                        except Branch.DoesNotExist:
                            pass

                    profile.first_name = request.POST.get('first_name', '').strip()
                    profile.last_name = request.POST.get('last_name', '').strip()
                    profile.phone = request.POST.get('phone', '').strip()
                    profile.address = request.POST.get('address', '').strip()
                    profile.save()
                    messages.success(request, f"'{username}' ({role}) qo'shildi.")
            else:
                messages.error(request, "Login va parol majburiy.")
        return redirect('admin_users')

    from .models import TelegramSettings
    tg = TelegramSettings.get()

    # Branch admin faqat o'z filialining foydalanuvchilarini ko'radi
    if is_branch_mgr:
        users = User.objects.filter(profile__branch=my_branch).prefetch_related('groups', 'profile__branch')
    else:
        users = User.objects.all().prefetch_related('groups', 'profile__branch')

    return render(request, 'admin_users.html', {
        'users': users,
        'branches': branches,
        'is_branch_mgr': is_branch_mgr,
        'my_branch': my_branch,
        'branch_allowed_roles': BRANCH_ALLOWED_ROLES,
        'tg': tg,
    })

@login_required
def dashboard(request):
    user = request.user

    # Non-superadmin users are redirected straight to their own section
    if not user.is_superuser:
        groups = set(user.groups.values_list('name', flat=True))
        if 'accountant' in groups:
            return redirect('accounting_dashboard')
        if 'hr' in groups:
            return redirect('hr_dashboard')
        if 'seller' in groups:
            return redirect('sales_dashboard')
        if 'production_manager' in groups:
            return redirect('production_dashboard')
        if 'branch_admin' in groups:
            return redirect('sales_dashboard')   # filial rahbari → sotuv bo'limi
        # Unknown role — show a plain access-denied page
        return render(request, 'no_access.html')

    # ── SuperAdmin only below ────────────────────────────────────────
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    today_production = ProductionLog.objects.filter(date__date=today).aggregate(total=Sum('quantity'))['total'] or 0
    yesterday_production = ProductionLog.objects.filter(date__date=yesterday).aggregate(total=Sum('quantity'))['total'] or 0

    today_pos_revenue = Sale.objects.filter(date__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    today_branch_revenue = BranchSale.objects.filter(date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    yesterday_pos_revenue = Sale.objects.filter(date__date=yesterday).aggregate(total=Sum('total_amount'))['total'] or 0
    yesterday_branch_revenue = BranchSale.objects.filter(date=yesterday).aggregate(total=Sum('total_amount'))['total'] or 0

    today_sales = Sale.objects.filter(date__date=today).count() + BranchSale.objects.filter(date=today).count()
    today_revenue = today_pos_revenue + today_branch_revenue
    yesterday_revenue = yesterday_pos_revenue + yesterday_branch_revenue
    revenue_delta = today_revenue - yesterday_revenue
    production_delta = today_production - yesterday_production

    # Collect last 4 months (including current month) for income/expense chart.
    month_start = today.replace(day=1)
    month_points = []
    for _ in range(4):
        month_points.append(month_start)
        month_start = (month_start - timedelta(days=1)).replace(day=1)
    month_points.reverse()

    tx_summary = (
        Transaction.objects.filter(date__date__gte=month_points[0])
        .annotate(month=TruncMonth('date'))
        .values('month', 'transaction_type')
        .annotate(total=Sum('amount'))
    )

    income_map = {}
    expense_map = {}
    for row in tx_summary:
        month_key = row['month'].date().isoformat()
        if row['transaction_type'] == 'income':
            income_map[month_key] = float(row['total'])
        elif row['transaction_type'] == 'expense':
            expense_map[month_key] = float(row['total'])

    revenue_labels = [point.strftime('%b %Y') for point in month_points]
    income_data = [income_map.get(point.isoformat(), 0) for point in month_points]
    expense_data = [expense_map.get(point.isoformat(), 0) for point in month_points]

    product_totals = {}
    for row in SaleItem.objects.values('product__name').annotate(total=Sum('quantity')).order_by('-total'):
        product_totals[row['product__name']] = (product_totals.get(row['product__name'], 0) + row['total'])
    for row in BranchSaleItem.objects.values('product__name').annotate(total=Sum('quantity')).order_by('-total'):
        product_totals[row['product__name']] = (product_totals.get(row['product__name'], 0) + row['total'])

    top_products_sorted = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_products_labels = [name for name, _ in top_products_sorted]
    top_products_data = [qty for _, qty in top_products_sorted]

    total_top_qty = sum(top_products_data) or 1
    top_products_rows = [
        {
            'name': name,
            'qty': qty,
            'share': round((qty / total_top_qty) * 100, 1),
        }
        for name, qty in top_products_sorted
    ]

    monthly_income_total = sum(income_data)
    monthly_expense_total = sum(expense_data)
    monthly_net_total = monthly_income_total - monthly_expense_total

    pos_sales_count = Sale.objects.filter(date__date=today).count()
    branch_sales_count = BranchSale.objects.filter(date=today).count()
    total_sales_count = pos_sales_count + branch_sales_count or 1
    pos_share_percent = round((pos_sales_count / total_sales_count) * 100, 1)
    branch_share_percent = round((branch_sales_count / total_sales_count) * 100, 1)

    recent_sales = Sale.objects.order_by('-date')[:6]
    recent_production_logs = ProductionLog.objects.select_related('product').order_by('-date')[:6]
    recent_transactions = Transaction.objects.select_related('cash_register').order_by('-date')[:8]
    cash_registers = CashRegister.objects.order_by('name')

    # Until a separate receivables model is introduced, branch sales are treated as receivables.
    debtors_total = BranchSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    creditors_total = Supplier.objects.aggregate(total=Sum('debt'))['total'] or 0
    cash_balances_total = CashRegister.objects.aggregate(total=Sum('balance'))['total'] or 0

    context = {
        'today_production': today_production,
        'today_sales': today_sales,
        'today_revenue': today_revenue,
        'yesterday_production': yesterday_production,
        'yesterday_revenue': yesterday_revenue,
        'revenue_delta': revenue_delta,
        'production_delta': production_delta,
        'debtors': debtors_total,
        'creditors': creditors_total,
        'cash_balances': cash_balances_total,
        'employees_on_shift': Employee.objects.filter(status='active').count(), # simplification for now
        'revenue_labels': revenue_labels,
        'income_data': income_data,
        'expense_data': expense_data,
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        'top_products_rows': top_products_rows,
        'monthly_income_total': monthly_income_total,
        'monthly_expense_total': monthly_expense_total,
        'monthly_net_total': monthly_net_total,
        'pos_sales_count': pos_sales_count,
        'branch_sales_count': branch_sales_count,
        'pos_share_percent': pos_share_percent,
        'branch_share_percent': branch_share_percent,
        'recent_sales': recent_sales,
        'recent_production_logs': recent_production_logs,
        'recent_transactions': recent_transactions,
        'cash_registers': cash_registers,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def save_telegram_settings(request):
    if not request.user.is_superuser:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    if request.method != 'POST':
        return redirect('admin_users')

    from .models import TelegramSettings
    tg = TelegramSettings.get()
    tg.bot_token = request.POST.get('bot_token', '').strip()
    tg.chat_id = request.POST.get('chat_id', '').strip()
    tg.is_active = request.POST.get('is_active') == 'on'
    tg.save()
    messages.success(request, "Telegram sozlamalari saqlandi.")
    return redirect('admin_users')


@login_required
def test_telegram(request):
    from django.http import JsonResponse
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)

    from .models import TelegramSettings
    import requests as http_req
    tg = TelegramSettings.get()
    token = tg.bot_token or ''
    chat_id = tg.chat_id or ''

    if not token or not chat_id:
        return JsonResponse({'error': 'Bot token yoki Chat ID kiritilmagan'})

    try:
        resp = http_req.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id,
                  'text': '✅ <b>NovvoyERP</b> — Telegram muvaffaqiyatli ulandi!',
                  'parse_mode': 'HTML'},
            timeout=8,
        )
        data = resp.json()
        if data.get('ok'):
            return JsonResponse({'success': True, 'message': 'Test xabari yuborildi!'})
        else:
            return JsonResponse({'error': data.get('description', 'Noma\'lum xato')})
    except Exception as e:
        return JsonResponse({'error': str(e)})
