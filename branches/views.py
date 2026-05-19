from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Branch, Transfer, TransferItem, BranchInventory, BranchSale, BranchSaleItem
from production.models import Product, FinishedGoodsInventory, ProductionLog


def _get_user_branch(user):
    """Returns the branch assigned to a branch_admin, or None for superadmin/admin."""
    if user.is_superuser or user.groups.filter(name='admin').exists():
        return None  # sees all
    try:
        return user.profile.branch
    except Exception:
        return None


def _can_access(user):
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['admin', 'accountant', 'seller', 'branch_admin']).exists()


@login_required
def branches_dashboard(request):
    if not _can_access(request.user):
        return redirect('dashboard')

    user_branch = _get_user_branch(request.user)
    is_branch_admin = (
        not request.user.is_superuser and
        request.user.groups.filter(name='branch_admin').exists()
    )

    # Scope querysets to the user's branch if branch_admin
    if user_branch:
        branches = Branch.objects.filter(id=user_branch.id)
        transfers = Transfer.objects.filter(branch=user_branch).select_related('branch').prefetch_related('items__product').order_by('-date_sent')[:20]
    else:
        branches = Branch.objects.all()
        transfers = Transfer.objects.select_related('branch').prefetch_related('items__product').order_by('-date_sent')[:20]

    products = Product.objects.all()

    from django.db.models import Sum

    total_branches = Branch.objects.count()
    in_transit_count = Transfer.objects.filter(status='in_transit').count()
    total_stock = BranchInventory.objects.aggregate(total=Sum('stock'))['total'] or 0

    branch_inventory_rows = []
    if user_branch:
        for inv in (
            BranchInventory.objects.filter(branch=user_branch, stock__gt=0)
            .select_related('product')
            .order_by('product__name')
        ):
            branch_inventory_rows.append(
                {'product': inv.product, 'stock': inv.stock}
            )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_branch':
            if is_branch_admin:
                messages.error(request, "Sizda filial qo'shish huquqi yo'q.")
                return redirect('branches_dashboard')
            name = request.POST.get('name', '').strip()
            address = request.POST.get('address', '').strip()
            responsible = request.POST.get('responsible_person', '').strip()
            if name:
                branch, created = Branch.objects.get_or_create(name=name, defaults={
                    'address': address, 'responsible_person': responsible,
                })
                if created:
                    messages.success(request, f"Filial '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' nomli filial allaqachon mavjud.")
            else:
                messages.error(request, "Filial nomi majburiy.")
            return redirect('branches_dashboard')

        elif action == 'delete_branch':
            if is_branch_admin:
                messages.error(request, "Sizda filial o'chirish huquqi yo'q.")
                return redirect('branches_dashboard')
            bid = request.POST.get('branch_id')
            try:
                Branch.objects.get(id=bid).delete()
                messages.success(request, "Filial o'chirildi.")
            except Branch.DoesNotExist:
                messages.error(request, "Filial topilmadi.")
            return redirect('branches_dashboard')

        elif 'create_transfer' in request.POST:
            if is_branch_admin:
                messages.error(request, "Sizda transfer yaratish huquqi yo'q.")
                return redirect('branches_dashboard')
            branch_id = request.POST.get('branch')
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity', 0))
            try:
                with transaction.atomic():
                    branch = Branch.objects.get(id=branch_id)
                    product = Product.objects.get(id=product_id)
                    fg = FinishedGoodsInventory.objects.get(product=product)
                    if fg.stock < quantity:
                        raise ValueError(f"Omborda {product.name} yetarli emas. Mavjud: {fg.stock}")
                    fg.stock -= quantity
                    fg.save()
                    transfer = Transfer.objects.create(branch=branch)
                    TransferItem.objects.create(transfer=transfer, product=product, quantity=quantity)
                    messages.success(request, f"{quantity} {product.name} → {branch.name} ga yuborildi.")
            except (Branch.DoesNotExist, Product.DoesNotExist):
                messages.error(request, "Filial yoki mahsulot topilmadi.")
            except FinishedGoodsInventory.DoesNotExist:
                messages.error(request, "Bu mahsulot omborida yo'q.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('branches_dashboard')

        elif 'receive_transfer' in request.POST:
            transfer_id = request.POST.get('transfer_id')
            try:
                with transaction.atomic():
                    transfer = Transfer.objects.get(id=transfer_id)
                    # branch_admin can only receive transfers for their own branch
                    if user_branch and transfer.branch != user_branch:
                        messages.error(request, "Bu transfer sizning filialingizga tegishli emas.")
                        return redirect('branches_dashboard')
                    transfer.status = 'received'
                    transfer.date_received = timezone.now()
                    transfer.save()
                    for item in transfer.items.all():
                        inv, _ = BranchInventory.objects.get_or_create(
                            branch=transfer.branch, product=item.product, defaults={'stock': 0}
                        )
                        inv.stock += item.quantity
                        inv.save()
                    messages.success(request, f"Transfer #{transfer.id} qabul qilindi.")
            except Transfer.DoesNotExist:
                messages.error(request, "Transfer topilmadi.")
            return redirect('branches_dashboard')

        elif 'add_branch_sale' in request.POST:
            # branch_admin records a sale for their branch (narx bazadagi mahsulot narxidan)
            if not user_branch:
                messages.error(request, "Faqat filial admini sotuv qo'sha oladi.")
                return redirect('branches_dashboard')
            from .models import BranchSale, BranchSaleItem
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity', 0))
            try:
                product = Product.objects.get(id=product_id)
                inv = BranchInventory.objects.get(branch=user_branch, product=product)
                price = product.price
                if quantity <= 0:
                    raise ValueError("Miqdor musbat bo‘lishi kerak.")
                if inv.stock < quantity:
                    raise ValueError(f"Qoldiq yetarli emas. Mavjud: {inv.stock}")
                with transaction.atomic():
                    inv.stock -= quantity
                    inv.save()
                    sale = BranchSale.objects.create(
                        branch=user_branch,
                        total_amount=price * quantity,
                    )
                    BranchSaleItem.objects.create(
                        branch_sale=sale,
                        product=product,
                        quantity=quantity,
                        price_at_sale=price,
                    )
                messages.success(request, f"Sotuv qayd etildi: {quantity} × {product.name}")
            except (Product.DoesNotExist, BranchInventory.DoesNotExist):
                messages.error(request, "Mahsulot yoki filial omborida topilmadi.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('branches_dashboard')

    # Inventory matrix
    inventory_matrix = []
    for branch in branches:
        branch_stocks = {inv.product_id: inv.stock for inv in branch.inventory.all()}
        inventory_matrix.append({
            'branch': branch,
            'stocks': [branch_stocks.get(p.id, 0) for p in products]
        })

    if is_branch_admin and user_branch:
        branch_labels = []
        branch_stock_data = []
    else:
        branch_labels = [b.name for b in Branch.objects.all()]
        branch_stock_data = [
            float(b.inventory.aggregate(total=Sum('stock'))['total'] or 0)
            for b in Branch.objects.all()
        ]

    # Sales for branch_admin's branch
    branch_sales = []
    if user_branch:
        from .models import BranchSale
        branch_sales = BranchSale.objects.filter(branch=user_branch).prefetch_related('items__product').order_by('-date')[:20]

    branch_stock_list = []
    if is_branch_admin and user_branch and inventory_matrix:
        r0 = inventory_matrix[0]
        branch_stock_list = list(zip(list(products), r0['stocks']))

    context = {
        'branches': branches,
        'products': products,
        'transfers': transfers,
        'total_branches': total_branches,
        'in_transit_count': in_transit_count,
        'total_stock': total_stock,
        'inventory_matrix': inventory_matrix,
        'branch_labels': branch_labels,
        'branch_stock_data': branch_stock_data,
        'user_branch': user_branch,
        'is_branch_admin': is_branch_admin,
        'branch_sales': branch_sales,
        'branch_inventory_rows': branch_inventory_rows,
        'branch_stock_list': branch_stock_list,
    }
    return render(request, 'branches.html', context)


@login_required
def branch_detail(request, branch_id):
    """Filial ichki paneli — sotuv, HR, buxgalteriya, ishlab chiqarish."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    branch = get_object_or_404(Branch, id=branch_id)

    today = timezone.localdate()
    week_ago = today - timedelta(days=6)
    month_start = today.replace(day=1)

    # ── Sotuv statistikasi ─────────────────────────────────────────────────────
    branch_sales_today = BranchSale.objects.filter(branch=branch, date=today)
    branch_sales_week  = BranchSale.objects.filter(branch=branch, date__gte=week_ago, date__lte=today)
    branch_sales_month = BranchSale.objects.filter(branch=branch, date__gte=month_start, date__lte=today)

    today_revenue = branch_sales_today.aggregate(t=Sum('total_amount'))['t'] or 0
    week_revenue  = branch_sales_week.aggregate(t=Sum('total_amount'))['t'] or 0
    month_revenue = branch_sales_month.aggregate(t=Sum('total_amount'))['t'] or 0

    # So'nggi 30 kun savdo tarixi
    recent_sales = (
        BranchSale.objects
        .filter(branch=branch)
        .prefetch_related('items__product')
        .order_by('-date', '-id')[:30]
    )

    # ── Omborxona ──────────────────────────────────────────────────────────────
    inventory = (
        BranchInventory.objects
        .filter(branch=branch)
        .select_related('product', 'product__category')
        .order_by('product__name')
    )
    total_stock_qty = inventory.aggregate(t=Sum('stock'))['t'] or 0
    low_stock = [i for i in inventory if 0 < i.stock < 10]

    # ── Transferlar ────────────────────────────────────────────────────────────
    in_transit = Transfer.objects.filter(branch=branch, status='in_transit').count()
    transfers = (
        Transfer.objects
        .filter(branch=branch)
        .prefetch_related('items__product')
        .order_by('-date_sent')[:20]
    )

    # ── HR — Xodimlar ──────────────────────────────────────────────────────────
    from hr.models import Employee, Attendance, DailyReport, FaceIDLog
    employees = Employee.objects.filter(branch=branch).select_related('shift').order_by('name')
    active_employees = employees.filter(status='active')

    # Bugungi davomat
    attendances_today = (
        Attendance.objects
        .filter(employee__branch=branch, date=today)
        .select_related('employee')
    )
    present_today = attendances_today.count()
    late_today    = attendances_today.filter(late_minutes__gt=0).count()

    # Bugungi hisobotlar
    daily_reports_today = (
        DailyReport.objects
        .filter(employee__branch=branch, date=today)
        .select_related('employee', 'shift')
    )

    # So'nggi Face ID loglari
    face_logs = (
        FaceIDLog.objects
        .filter(employee__branch=branch, timestamp__date=today)
        .select_related('employee')
        .order_by('-timestamp')[:15]
    )

    # ── Buxgalteriya ───────────────────────────────────────────────────────────
    from accounting.models import Transaction, CashRegister
    # Filialga tegishli tranzaktsiyalar (branch_admin uzerlar orqali)
    branch_user_ids = list(
        branch.admins.values_list('user_id', flat=True)
    )
    transactions = (
        Transaction.objects
        .filter(created_by_id__in=branch_user_ids) if branch_user_ids
        else Transaction.objects.none()
    )
    # Oddiy: barcha branch sotuvlari orqali daromad hisoblash
    month_income  = month_revenue  # BranchSale asosida
    today_income  = today_revenue

    # ── Ishlab chiqarish ───────────────────────────────────────────────────────
    # Filial xodimlari nomi bo'yicha ishlab chiqarish loglari
    emp_names = list(employees.values_list('name', flat=True))
    production_today = (
        ProductionLog.objects
        .filter(date__date=today, baker_name__in=emp_names)
        .select_related('product')
        .order_by('-date')
    )
    production_month = (
        ProductionLog.objects
        .filter(date__date__gte=month_start, baker_name__in=emp_names)
    )
    production_today_qty = production_today.aggregate(t=Sum('quantity'))['t'] or 0
    production_month_qty = production_month.aggregate(t=Sum('quantity'))['t'] or 0

    # Mahsulot bo'yicha bugungi ishlab chiqarish
    production_by_product = (
        production_today
        .values('product__name')
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')[:10]
    )

    context = {
        'branch': branch,
        'today': today,
        # Sotuv
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'recent_sales': recent_sales,
        # Omborxona
        'inventory': inventory,
        'total_stock_qty': total_stock_qty,
        'low_stock': low_stock,
        # Transferlar
        'transfers': transfers,
        'in_transit': in_transit,
        # HR
        'employees': employees,
        'active_employees_count': active_employees.count(),
        'attendances_today': attendances_today,
        'present_today': present_today,
        'late_today': late_today,
        'daily_reports_today': daily_reports_today,
        'face_logs': face_logs,
        # Buxgalteriya
        'today_income': today_income,
        'month_income': month_income,
        # Ishlab chiqarish
        'production_today_qty': production_today_qty,
        'production_month_qty': production_month_qty,
        'production_today': production_today,
        'production_by_product': production_by_product,
        # Transfer shakli
        'all_products': Product.objects.all().order_by('name'),
    }
    return render(request, 'branch_detail.html', context)
