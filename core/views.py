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
def admin_users(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    _ensure_groups()
    branches = Branch.objects.all()
    if request.method == 'POST':
        if request.POST.get('delete_user_id'):
            uid = request.POST.get('delete_user_id')
            try:
                u = User.objects.get(id=uid)
                if u != request.user:
                    u.delete()
                    messages.success(request, "Foydalanuvchi o'chirildi.")
            except User.DoesNotExist:
                pass
        elif request.POST.get('action') == 'create_branch_with_admin':
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
            if username and password:
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Bu login allaqachon mavjud.")
                else:
                    is_super = role == 'superadmin'
                    u = User.objects.create_user(
                        username=username,
                        password=password,
                        is_superuser=is_super,
                        is_staff=is_super,
                    )
                    if not is_super:
                        group, _ = Group.objects.get_or_create(name=role)
                        u.groups.add(group)
                    profile = UserProfile.objects.create(user=u)
                    if role == 'branch_admin' and branch_id:
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
    users = User.objects.all().prefetch_related('groups', 'profile__branch')
    return render(request, 'admin_users.html', {'users': users, 'branches': branches})

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
            return redirect('branches_dashboard')
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
