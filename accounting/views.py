from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from branches.models import BranchSale
from sales.models import Sale

from .models import Account, CashRegister, ExpenseCategory, JournalEntry, JournalLine, Supplier, Transaction
from . import chart_data, services


def _can_access(user, *roles):
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def _get_user_branch(user):
    """Branch_admin bo'lsa filialni, aks holda None qaytaradi."""
    if user.is_superuser:
        return None
    if user.groups.filter(name='branch_admin').exists():
        try:
            return user.profile.branch
        except Exception:
            return None
    return None


def _month_bounds(d):
    first = d.replace(day=1)
    if first.month == 12:
        nxt = first.replace(year=first.year + 1, month=1)
    else:
        nxt = first.replace(month=first.month + 1)
    last = nxt - timedelta(days=1)
    return first, last


def _preset_range(request, preset):
    today = timezone.localdate()
    if preset == 'today':
        return today, today
    if preset == 'yesterday':
        y = today - timedelta(days=1)
        return y, y
    if preset == 'today_yesterday':
        return today - timedelta(days=1), today
    if preset == 'last_7':
        return today - timedelta(days=6), today
    if preset == 'last_14':
        return today - timedelta(days=13), today
    if preset == 'last_28':
        return today - timedelta(days=27), today
    if preset == 'last_30':
        return today - timedelta(days=29), today
    if preset == 'this_week':
        start = today - timedelta(days=today.weekday())
        return start, today
    if preset == 'last_week':
        this_week_start = today - timedelta(days=today.weekday())
        last_week_end = this_week_start - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)
        return last_week_start, last_week_end
    if preset == 'this_month':
        start, end = _month_bounds(today)
        return start, min(end, today)
    if preset == 'last_month':
        this_month_start, _ = _month_bounds(today)
        prev_month_day = this_month_start - timedelta(days=1)
        return _month_bounds(prev_month_day)
    if preset == 'maximum':
        first_candidates = [
            Transaction.objects.order_by('date').values_list('date', flat=True).first(),
            JournalEntry.objects.order_by('entry_date').values_list('entry_date', flat=True).first(),
            Sale.objects.order_by('date').values_list('date', flat=True).first(),
            BranchSale.objects.order_by('date').values_list('date', flat=True).first(),
        ]
        first_dates = []
        for dt in first_candidates:
            if not dt:
                continue
            if hasattr(dt, 'date'):
                first_dates.append(dt.date())
            else:
                first_dates.append(dt)
        if first_dates:
            return min(first_dates), today
        return today, today
    return today, today


def _date_range(request):
    saved = request.session.get('accounting_saved_filter') or {}
    has_query_filter = any(
        request.GET.get(k)
        for k in ('preset', 'period', 'date_from', 'date_to')
    )

    preset = request.GET.get('preset') or request.GET.get('period')
    if not preset and not has_query_filter and saved:
        preset = saved.get('preset') or 'today'
        saved_df = saved.get('date_from')
        saved_dt = saved.get('date_to')
        if preset == 'custom' and saved_df and saved_dt:
            try:
                return 'custom', date.fromisoformat(saved_df), date.fromisoformat(saved_dt)
            except ValueError:
                pass

    preset = preset or 'today'
    if preset == 'custom':
        try:
            df = date.fromisoformat(request.GET.get('date_from', ''))
            dt = date.fromisoformat(request.GET.get('date_to', ''))
            if dt < df:
                df, dt = dt, df
            return 'custom', df, dt
        except ValueError:
            return 'today', timezone.localdate(), timezone.localdate()

    df, dt = _preset_range(request, preset)
    return preset, df, dt


@login_required
def accounting_dashboard(request):
    if not _can_access(request.user, 'accountant', 'branch_admin'):
        return redirect('dashboard')

    user_branch = _get_user_branch(request.user)

    services.ensure_control_accounts()
    services.backfill_gl_for_existing_registers()

    period, date_from, date_to = _date_range(request)
    if request.GET.get('save_range') == '1':
        request.session['accounting_saved_filter'] = {
            'preset': period,
            'date_from': date_from.isoformat(),
            'date_to': date_to.isoformat(),
        }
        request.session.modified = True
    start_dt = timezone.make_aware(datetime.combine(date_from, time.min))
    end_dt = timezone.make_aware(datetime.combine(date_to + timedelta(days=1), time.min))

    # Branch_admin faqat o'z filiali ma'lumotlarini ko'radi
    if user_branch:
        registers = CashRegister.objects.filter(branch=user_branch).select_related('gl_account').order_by('name')
        tx_window_qs = Transaction.objects.filter(branch=user_branch, date__gte=start_dt, date__lt=end_dt)
    else:
        # Superadmin/accountant: filtrash imkoniyati
        branch_filter = request.GET.get('branch_filter', '')
        if branch_filter and request.user.is_superuser:
            from branches.models import Branch as BranchModel
            try:
                fb = BranchModel.objects.get(id=branch_filter)
                registers = CashRegister.objects.filter(branch=fb).select_related('gl_account').order_by('name')
                tx_window_qs = Transaction.objects.filter(branch=fb, date__gte=start_dt, date__lt=end_dt)
            except Exception:
                registers = CashRegister.objects.filter(branch__isnull=True).select_related('gl_account').order_by('name', 'id')
                tx_window_qs = Transaction.objects.filter(branch__isnull=True, date__gte=start_dt, date__lt=end_dt)
        else:
            # default: asosiy ofis (branch=None)
            registers = CashRegister.objects.filter(branch__isnull=True).select_related('gl_account').order_by('name', 'id')
            tx_window_qs = Transaction.objects.filter(branch__isnull=True, date__gte=start_dt, date__lt=end_dt)

    je_window_qs = JournalEntry.objects.filter(entry_date__gte=start_dt, entry_date__lt=end_dt)
    expense_cats = ExpenseCategory.objects.all()
    suppliers = Supplier.objects.all()
    accounts = Account.objects.filter(is_active=True).order_by('code')

    recent_transactions = tx_window_qs.select_related(
        'cash_register', 'expense_category', 'supplier'
    ).order_by('-date')[:80]
    journal_entries = (
        je_window_qs.select_related('created_by', 'transaction')
        .prefetch_related('lines__account')
        .order_by('-entry_date')[:35]
    )
    ledger_tx_total = tx_window_qs.count()
    ledger_je_total = je_window_qs.count()
    ledger_line_total = JournalLine.objects.filter(entry__in=je_window_qs).count()
    tb_qs = (
        JournalLine.objects.filter(entry__entry_date__gte=start_dt, entry__entry_date__lt=end_dt)
        .values('account__code', 'account__name', 'account__account_type')
        .annotate(debit_total=Sum('debit'), credit_total=Sum('credit'))
        .order_by('account__code')
    )
    tb = [
        {
            'code': r['account__code'],
            'name': r['account__name'],
            'type': r['account__account_type'],
            'debit': r['debit_total'] or Decimal('0'),
            'credit': r['credit_total'] or Decimal('0'),
        }
        for r in tb_qs
    ]
    tb_total_d = sum(r['debit'] for r in tb)
    tb_total_c = sum(r['credit'] for r in tb)
    tb_balanced = tb_total_d == tb_total_c

    now = timezone.now()
    today = now.date()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    cash_register_rows = services.cash_register_rows_from_registers(registers)
    total_balance = sum((r['balance'] for r in cash_register_rows), Decimal('0'))
    total_debt = suppliers.aggregate(total=Sum('debt'))['total'] or Decimal('0')

    period_income = Transaction.objects.filter(
        transaction_type='income', date__gte=start_dt, date__lt=end_dt
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    period_expense = Transaction.objects.filter(
        transaction_type__in=['expense', 'supplier_payment'], date__gte=start_dt, date__lt=end_dt
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    pos_today = Sale.objects.filter(date__date=today).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    pos_month = Sale.objects.filter(date__gte=first_of_month).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    br_today = BranchSale.objects.filter(date=today).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    br_month = BranchSale.objects.filter(date__gte=first_of_month.date()).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    pos_period = Sale.objects.filter(date__date__gte=date_from, date__date__lte=date_to).aggregate(
        t=Sum('total_amount')
    )['t'] or Decimal('0')
    br_period = BranchSale.objects.filter(date__gte=date_from, date__lte=date_to).aggregate(
        t=Sum('total_amount')
    )['t'] or Decimal('0')

    monthly_net = period_income - period_expense
    combined_sales_today = pos_today + br_today
    combined_sales_month = pos_period + br_period

    tx_month_count = tx_window_qs.count()
    je_month_count = je_window_qs.count()
    journal_lines_month = JournalLine.objects.filter(entry__entry_date__gte=start_dt, entry__entry_date__lt=end_dt).count()
    suppliers_with_debt_count = Supplier.objects.filter(debt__gt=0).count()
    account_count = accounts.count()
    pos_all_time_total = Sale.objects.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')

    overview_kpis = [
        {
            'label': "Jami kassa qoldigi",
            'value': total_balance,
            'kind': 'money',
            'icon': 'fa-wallet',
            'hint': "Har kassa uchun jurnal (GL) aktiv balansi; yig'indi",
        },
        {
            'label': 'Ta\'minotchilar qarzi',
            'value': total_debt,
            'kind': 'money',
            'icon': 'fa-hand-holding-dollar',
            'hint': 'Kreditorlik balansi',
        },
        {
            'label': 'Davr kassa tushumi',
            'value': period_income,
            'kind': 'money',
            'icon': 'fa-arrow-trend-up',
            'hint': 'Tanlangan davrda kassaga tushgan',
        },
        {
            'label': 'Davr kassa chiqimi',
            'value': period_expense,
            'kind': 'money',
            'icon': 'fa-arrow-trend-down',
            'hint': "Xarajat va ta\'minotchiga to'lov",
        },
        {
            'label': 'Davr sof pul oqimi',
            'value': monthly_net,
            'kind': 'money',
            'icon': 'fa-scale-balanced',
            'hint': 'Tushum − chiqim (tanlangan davr)',
        },
        {
            'label': 'Bugungi POS savdosi',
            'value': pos_today,
            'kind': 'money',
            'icon': 'fa-cash-register',
            'hint': 'sales.Sale — bugun',
        },
        {
            'label': 'Bugungi filial savdosi',
            'value': br_today,
            'kind': 'money',
            'icon': 'fa-store',
            'hint': 'branches.BranchSale — bugun',
        },
        {
            'label': 'Bugun jami savdo',
            'value': combined_sales_today,
            'kind': 'money',
            'icon': 'fa-coins',
            'hint': 'POS + filial (bugun)',
        },
        {
            'label': 'Davr savdo (POS+filial)',
            'value': combined_sales_month,
            'kind': 'money',
            'icon': 'fa-chart-line',
            'hint': 'Tanlangan davr umumiy savdo',
        },
        {
            'label': 'Davr kassa operatsiyalari',
            'value': tx_month_count,
            'kind': 'int',
            'icon': 'fa-receipt',
            'hint': 'Transaction yozuvlari soni',
        },
        {
            'label': 'Davr jurnal yozuvlari',
            'value': je_month_count,
            'kind': 'int',
            'icon': 'fa-book',
            'hint': 'JournalEntry — joriy oy',
        },
        {
            'label': 'Davr jurnal qatorlari',
            'value': journal_lines_month,
            'kind': 'int',
            'icon': 'fa-list-ol',
            'hint': 'JournalLine — joriy oy',
        },
        {
            'label': 'Faol GL hisoblari',
            'value': account_count,
            'kind': 'int',
            'icon': 'fa-sitemap',
            'hint': 'Hisoblar rejasi',
        },
        {
            'label': 'Qarzdor ta\'minotchilar',
            'value': suppliers_with_debt_count,
            'kind': 'int',
            'icon': 'fa-truck-field',
            'hint': 'Qarzi > 0',
        },
        {
            'label': 'Umumiy POS aylanmasi',
            'value': pos_all_time_total,
            'kind': 'money',
            'icon': 'fa-file-invoice-dollar',
            'hint': 'Barcha vaqtlar POS tushumi',
        },
    ]

    register_labels = [r['name'] for r in cash_register_rows]
    register_data = [float(r['balance']) for r in cash_register_rows]

    chart_bundle = chart_data.build_overview_chart_bundle(
        first_of_month,
        today,
        tb_total_d,
        tb_total_c,
        register_labels,
        register_data,
    )
    chart_cards = [
        {'key': 'trend_6m', 'title': 'Oylik kassa oqimi', 'hint': "So'nggi 6 oy — tushum va chiqim (Transaction)"},
        {'key': 'register_split', 'title': 'Kassalar taqsimoti', 'hint': 'Kassa qoldiqlari'},
        {'key': 'pos_vs_branch_6m', 'title': 'POS va filial savdosi', 'hint': '6 oylik solishtirish'},
        {'key': 'daily_sales_14d', 'title': 'Kunlik savdo (14 kun)', 'hint': 'POS + filial'},
        {'key': 'tx_type_pie', 'title': 'Kassa operatsiyalari (oy)', 'hint': "Turlar bo'yicha summa"},
        {'key': 'expense_categories', 'title': 'Xarajat kategoriyalari', 'hint': 'Joriy oy'},
        {'key': 'supplier_debt', 'title': 'Ta\'minotchi qarzlari', 'hint': 'TOP 10'},
        {'key': 'payment_methods', 'title': "POS to'lov usullari", 'hint': "Oy bo'yicha"},
        {'key': 'top_products', 'title': 'TOP mahsulotlar', 'hint': 'Oy daromadi (POS)'},
        {'key': 'branch_sales_month', 'title': 'Filial savdosi', 'hint': 'Joriy oy'},
        {'key': 'journal_daily_14', 'title': 'Kunlik jurnal', 'hint': "14 kun — yozuvlar soni"},
        {'key': 'gl_activity', 'title': 'GL faolligi', 'hint': "Hisoblar bo'yicha (oy)"},
        {'key': 'hourly_pos_today', 'title': 'Bugungi POS (soat)', 'hint': 'Bugun'},
        {'key': 'tx_type_counts', 'title': 'Operatsiya turlari soni', 'hint': 'Oy'},
        {'key': 'trial_balance_split', 'title': 'Sinov balansi', 'hint': 'Jami debet / kredit'},
    ]

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_register':
            name = request.POST.get('name', '').strip()
            try:
                bal = Decimal(request.POST.get('initial_balance', '0') or '0')
            except InvalidOperation:
                bal = Decimal('0')
            if name:
                if CashRegister.objects.filter(name=name, branch=user_branch).exists():
                    messages.warning(request, f"«{name}» allaqachon mavjud.")
                else:
                    reg = CashRegister.objects.create(name=name, balance=Decimal('0'), branch=user_branch)
                    services.ensure_register_gl(reg)
                    if bal > 0:
                        try:
                            services.record_income(reg, bal, request.user, "Boshlang'ich qoldiq")
                        except Exception as e:
                            messages.warning(request, f"Kassa yaratildi, boshlang'ich jurnal xatosi: {e}")
                    messages.success(request, f"Kassa «{name}» qo'shildi.")
            else:
                messages.error(request, 'Kassa nomi majburiy.')

        elif action == 'add_category':
            name = request.POST.get('name', '').strip()
            if name:
                cat, created = ExpenseCategory.objects.get_or_create(name=name)
                if created:
                    messages.success(request, f"Kategoriya «{name}» qo'shildi.")
                else:
                    messages.warning(request, 'Bu kategoriya allaqachon bor.')
            else:
                messages.error(request, 'Kategoriya nomi majburiy.')

        elif action == 'add_supplier':
            name = request.POST.get('name', '').strip()
            contact = request.POST.get('contact', '').strip()
            if name:
                sup, created = Supplier.objects.get_or_create(name=name, defaults={'contact_info': contact})
                if not created and contact:
                    sup.contact_info = contact
                    sup.save(update_fields=['contact_info'])
                if created:
                    messages.success(request, f"Ta'minotchi «{name}» qo'shildi.")
                else:
                    messages.warning(request, 'Bu nom allaqachon mavjud.')
            else:
                messages.error(request, 'Ta\'minotchi nomi majburiy.')

        elif action == 'delete_register':
            rid = request.POST.get('register_id')
            try:
                CashRegister.objects.get(id=rid).delete()
                messages.success(request, "Kassa o'chirildi.")
            except CashRegister.DoesNotExist:
                messages.error(request, 'Kassa topilmadi.')

        elif action == 'delete_category':
            cid = request.POST.get('category_id')
            try:
                ExpenseCategory.objects.get(id=cid).delete()
                messages.success(request, "Kategoriya o'chirildi.")
            except ExpenseCategory.DoesNotExist:
                messages.error(request, 'Kategoriya topilmadi.')

        elif action == 'delete_supplier':
            sid = request.POST.get('supplier_id')
            try:
                Supplier.objects.get(id=sid).delete()
                messages.success(request, "Ta\'minotchi o'chirildi.")
            except Supplier.DoesNotExist:
                messages.error(request, 'Topilmadi.')

        elif request.POST.get('add_income'):
            try:
                amount = Decimal(request.POST.get('amount', '0'))
                rid = request.POST.get('register')
                desc = request.POST.get('description', '').strip()
                reg = CashRegister.objects.get(id=rid)
                services.record_income(reg, amount, request.user, desc)
                messages.success(request, f"{amount:,.0f} UZS kassaga qayd etildi.")
            except (CashRegister.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, str(e) if str(e) else 'Xato.')

        elif request.POST.get('add_expense'):
            try:
                amount = Decimal(request.POST.get('amount', '0'))
                reg = CashRegister.objects.get(id=request.POST.get('register'))
                cat = ExpenseCategory.objects.get(id=request.POST.get('category'))
                desc = request.POST.get('description', '').strip()
                services.record_expense(reg, amount, cat, request.user, desc)
                messages.success(request, f"{amount:,.0f} UZS xarajat qayd etildi.")
            except (CashRegister.DoesNotExist, ExpenseCategory.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, str(e) if str(e) else 'Xato.')

        elif request.POST.get('transfer_funds'):
            try:
                amount = Decimal(request.POST.get('amount', '0'))
                from_reg = CashRegister.objects.get(id=request.POST.get('from_register'))
                to_reg = CashRegister.objects.get(id=request.POST.get('to_register'))
                desc = request.POST.get('description', '').strip()
                if from_reg.id == to_reg.id:
                    messages.error(request, "Manba va maqsad kassa bir xil bo'lmasligi kerak.")
                else:
                    services.record_transfer(from_reg, to_reg, amount, request.user, desc)
                    messages.success(request, "O'tkazma bajarildi.")
            except (CashRegister.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, str(e) if str(e) else 'Xato.')

        elif request.POST.get('supplier_payment'):
            try:
                amount = Decimal(request.POST.get('amount', '0'))
                reg = CashRegister.objects.get(id=request.POST.get('register'))
                sup = Supplier.objects.get(id=request.POST.get('supplier'))
                services.record_supplier_payment(reg, sup, amount, request.user)
                messages.success(request, "To'lov qayd etildi.")
            except (CashRegister.DoesNotExist, Supplier.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, str(e) if str(e) else 'Xato.')

        elif request.POST.get('supplier_debt'):
            try:
                amount = Decimal(request.POST.get('amount', '0'))
                sup = Supplier.objects.get(id=request.POST.get('supplier'))
                desc = request.POST.get('description', '').strip()
                services.record_supplier_debt_increase(sup, amount, request.user, desc)
                messages.success(request, 'Qarzga xarid jurnalga yozildi.')
            except (Supplier.DoesNotExist, InvalidOperation, ValueError) as e:
                messages.error(request, str(e) if str(e) else 'Xato.')

        elif request.POST.get('manual_journal'):
            memo = request.POST.get('mj_memo', '').strip()
            ref = request.POST.get('mj_ref', '').strip()
            rows = []
            for i in range(1, 9):
                aid = request.POST.get(f'acc_{i}')
                if not aid:
                    continue
                rows.append(
                    {
                        'account_id': aid,
                        'debit': request.POST.get(f'd_{i}', '0'),
                        'credit': request.POST.get(f'c_{i}', '0'),
                        'description': request.POST.get(f'n_{i}', ''),
                    }
                )
            try:
                services.post_manual_journal(request.user, memo, ref, rows)
                messages.success(request, "Qo'lda jurnal yozuvi yaratildi.")
            except Exception as e:
                messages.error(request, str(e))

        return redirect('accounting_dashboard')

    # Superadmin uchun filiallar ro'yxati (filtr uchun)
    from branches.models import Branch as BranchModel
    all_branches_for_filter = []
    current_branch_filter = None
    if request.user.is_superuser:
        all_branches_for_filter = list(BranchModel.objects.order_by('name'))
        branch_filter_id = request.GET.get('branch_filter', '')
        if branch_filter_id:
            current_branch_filter = BranchModel.objects.filter(id=branch_filter_id).first()

    context = {
        'registers': registers,
        'cash_register_rows': cash_register_rows,
        'expense_cats': expense_cats,
        'suppliers': suppliers,
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'journal_entries': journal_entries,
        'trial_balance': tb,
        'tb_total_debit': tb_total_d,
        'tb_total_credit': tb_total_c,
        'tb_balanced': tb_balanced,
        'total_balance': total_balance,
        'total_debt': total_debt,
        'monthly_income': period_income,
        'monthly_expense': period_expense,
        'chart_bundle': chart_bundle,
        'chart_cards': chart_cards,
        'pos_today': pos_today,
        'pos_month': pos_month,
        'pos_period': pos_period,
        'br_today': br_today,
        'br_month': br_month,
        'br_period': br_period,
        'overview_kpis': overview_kpis,
        'ledger_tx_total': ledger_tx_total,
        'ledger_je_total': ledger_je_total,
        'ledger_line_total': ledger_line_total,
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'saved_filter': request.session.get('accounting_saved_filter'),
        'user_branch': user_branch,
        'all_branches_for_filter': all_branches_for_filter,
        'current_branch_filter': current_branch_filter,
    }
    return render(request, 'accounting.html', context)
