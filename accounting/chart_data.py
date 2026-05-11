"""
Buxgalteriya «Ko‘rinish» diagrammalari — barcha qiymatlar ma’lumotlar bazasidan.
"""
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncHour
from django.utils import timezone

from branches.models import BranchSale
from sales.models import Sale, SaleItem

from .models import JournalEntry, JournalLine, Supplier, Transaction


def _f(x):
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    return float(x)


def _month_starts_for_last_n_months(n: int, today):
    """Oxirgi n oyning birinchi kunlari (eskidan yangiga)."""
    y, m = today.year, today.month
    months = []
    for i in range(n - 1, -1, -1):
        mm = m - i
        yy = y
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm, datetime(yy, mm, 1).date()))
    return months


def _range_for_month(yy, mm):
    d0 = datetime(yy, mm, 1).date()
    start = timezone.make_aware(datetime.combine(d0, datetime.min.time()))
    if mm == 12:
        end_d = datetime(yy + 1, 1, 1).date()
    else:
        end_d = datetime(yy, mm + 1, 1).date()
    end = timezone.make_aware(datetime.combine(end_d, datetime.min.time()))
    return start, end, d0


def build_overview_chart_bundle(first_of_month, today, tb_total_debit, tb_total_credit, register_labels, register_data):
    """
    Chart.js uchun serializatsiya qilingan ma’lumotlar to‘plami.
    Barcha summalar va sonlar float/int.
    """
    months = _month_starts_for_last_n_months(6, today)

    # 1–2: 6 oy kassa tushum/chiqim (Transaction)
    labels_6m = []
    income_6m = []
    expense_6m = []
    pos_6m = []
    br_6m = []
    for yy, mm, d0 in months:
        labels_6m.append(d0.strftime('%b %Y'))
        start, end, _ = _range_for_month(yy, mm)
        inc = Transaction.objects.filter(transaction_type='income', date__gte=start, date__lt=end).aggregate(
            t=Sum('amount')
        )['t'] or Decimal('0')
        exp = Transaction.objects.filter(
            transaction_type__in=['expense', 'supplier_payment'], date__gte=start, date__lt=end
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        income_6m.append(_f(inc))
        expense_6m.append(_f(exp))
        p = Sale.objects.filter(date__gte=start, date__lt=end).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        b = BranchSale.objects.filter(date__gte=start.date(), date__lt=end.date()).aggregate(
            t=Sum('total_amount')
        )['t'] or Decimal('0')
        pos_6m.append(_f(p))
        br_6m.append(_f(b))

    # 3: so‘nggi 14 kun kunlik savdo (POS + filial)
    labels_14d = []
    pos_14 = []
    br_14 = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        labels_14d.append(d.strftime('%d.%m'))
        p = Sale.objects.filter(date__date=d).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        b = BranchSale.objects.filter(date=d).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        pos_14.append(_f(p))
        br_14.append(_f(b))

    # 4: oy operatsiya turlari bo‘yicha summa (pie)
    tx_type_labels = []
    tx_type_vals = []
    type_map = {
        'income': 'Tushum',
        'expense': 'Xarajat',
        'transfer': 'O‘tkazma',
        'supplier_payment': 'Ta\'minotchi to‘lovi',
    }
    for row in (
        Transaction.objects.filter(date__gte=first_of_month)
        .values('transaction_type')
        .annotate(s=Sum('amount'))
        .order_by('-s')
    ):
        tx_type_labels.append(type_map.get(row['transaction_type'], row['transaction_type']))
        tx_type_vals.append(_f(row['s']))

    if not tx_type_labels:
        tx_type_labels = ['—']
        tx_type_vals = [0.0]

    # 5: xarajat kategoriyalari (oy)
    exp_rows = list(
        Transaction.objects.filter(
            date__gte=first_of_month,
            transaction_type='expense',
            expense_category__isnull=False,
        )
        .values('expense_category__name')
        .annotate(s=Sum('amount'))
        .order_by('-s')[:10]
    )
    exp_cat_labels = [r['expense_category__name'] or '—' for r in exp_rows]
    exp_cat_vals = [_f(r['s']) for r in exp_rows]
    if not exp_cat_labels:
        exp_cat_labels = ['Ma’lumot yo‘q']
        exp_cat_vals = [0.0]

    # 6: ta'minotchilar qarzi TOP
    sup_rows = list(Supplier.objects.filter(debt__gt=0).order_by('-debt')[:10])
    sup_labels = [s.name[:28] for s in sup_rows]
    sup_vals = [_f(s.debt) for s in sup_rows]
    if not sup_labels:
        sup_labels = ['—']
        sup_vals = [0.0]

    # 7: POS to‘lov usullari (oy)
    pm_map = {'cash': 'Naqd', 'terminal': 'Terminal', 'electronic': 'Elektron'}
    pm_labels = []
    pm_vals = []
    for row in (
        Sale.objects.filter(date__gte=first_of_month)
        .values('payment_method')
        .annotate(s=Sum('total_amount'))
        .order_by('-s')
    ):
        pm_labels.append(pm_map.get(row['payment_method'], row['payment_method'] or '—'))
        pm_vals.append(_f(row['s']))
    if not pm_labels:
        pm_labels = ['—']
        pm_vals = [0.0]

    # 8: TOP mahsulotlar (oy daromad)
    prod_rows = list(
        SaleItem.objects.filter(sale__date__gte=first_of_month)
        .annotate(
            line_rev=ExpressionWrapper(
                F('quantity') * F('price_at_sale'),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        )
        .values('product__name')
        .annotate(revenue=Sum('line_rev'))
        .order_by('-revenue')[:10]
    )
    prod_labels = [(r['product__name'] or '—')[:24] for r in prod_rows]
    prod_vals = [_f(r['revenue']) for r in prod_rows]
    if not prod_labels:
        prod_labels = ['—']
        prod_vals = [0.0]

    # 9: filial bo‘yicha savdo (oy)
    br_rows = list(
        BranchSale.objects.filter(date__gte=first_of_month.date())
        .values('branch__name')
        .annotate(s=Sum('total_amount'))
        .order_by('-s')[:12]
    )
    br_name_labels = [r['branch__name'] or '—' for r in br_rows]
    br_sale_vals = [_f(r['s']) for r in br_rows]
    if not br_name_labels:
        br_name_labels = ['—']
        br_sale_vals = [0.0]

    # 10: kunlik jurnal yozuvlari (14 kun)
    je_labels = []
    je_counts = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        je_labels.append(d.strftime('%d.%m'))
        start_d = timezone.make_aware(datetime.combine(d, datetime.min.time()))
        end_d = timezone.make_aware(datetime.combine(d + timedelta(days=1), datetime.min.time()))
        c = JournalEntry.objects.filter(entry_date__gte=start_d, entry_date__lt=end_d).count()
        je_counts.append(c)

    # 11: GL hisoblar bo‘yicha faollik (oy, debet+kredit yig‘indisi)
    gl_rows = list(
        JournalLine.objects.filter(entry__entry_date__gte=first_of_month)
        .values('account__code', 'account__name')
        .annotate(
            d=Sum('debit'),
            c=Sum('credit'),
        )
    )
    gl_rows.sort(
        key=lambda r: float((r['d'] or Decimal('0')) + (r['c'] or Decimal('0'))),
        reverse=True,
    )
    gl_rows = gl_rows[:12]
    gl_labels = []
    gl_vals = []
    for r in gl_rows:
        code = r['account__code'] or ''
        name = (r['account__name'] or '')[:16]
        gl_labels.append(f"{code} {name}".strip() or '—')
        gl_vals.append(_f((r['d'] or Decimal('0')) + (r['c'] or Decimal('0'))))
    if not gl_labels:
        gl_labels = ['—']
        gl_vals = [0.0]

    # 12: bugungi POS soatlik
    hourly_labels = []
    hourly_vals = []
    hr_data = (
        Sale.objects.filter(date__date=today)
        .annotate(hour=TruncHour('date'))
        .values('hour')
        .annotate(s=Sum('total_amount'))
        .order_by('hour')
    )
    for row in hr_data:
        h = row['hour']
        if h is not None:
            hourly_labels.append(h.astimezone(timezone.get_current_timezone()).strftime('%H:%M'))
        else:
            hourly_labels.append('—')
        hourly_vals.append(_f(row['s']))
    if not hourly_labels:
        hourly_labels = ['Ma’lumot yo‘q']
        hourly_vals = [0.0]

    # 13: operatsiya turlari soni (oy)
    cnt_labels = []
    cnt_vals = []
    for row in (
        Transaction.objects.filter(date__gte=first_of_month)
        .values('transaction_type')
        .annotate(c=Count('id'))
        .order_by('-c')
    ):
        cnt_labels.append(type_map.get(row['transaction_type'], row['transaction_type']))
        cnt_vals.append(int(row['c'] or 0))
    if not cnt_labels:
        cnt_labels = ['—']
        cnt_vals = [0]

    # 14: sinov balansi (jami debet / kredit) — jurnaldan
    tb_d = _f(tb_total_debit)
    tb_c = _f(tb_total_credit)

    common_opts = {
        'responsive': True,
        'maintainAspectRatio': False,
        'plugins': {'legend': {'labels': {'font': {'family': 'Manrope', 'size': 11}}}},
    }

    return {
        'trend_6m': {
            'type': 'bar',
            'data': {
                'labels': labels_6m,
                'datasets': [
                    {'label': 'Kassa tushum', 'data': income_6m, 'backgroundColor': 'rgba(40, 167, 69, 0.55)', 'borderRadius': 6},
                    {'label': 'Kassa chiqim', 'data': expense_6m, 'backgroundColor': 'rgba(220, 53, 69, 0.45)', 'borderRadius': 6},
                ],
            },
            'options': {**common_opts, 'scales': {'x': {'grid': {'display': False}}, 'y': {'beginAtZero': True}}},
        },
        'register_split': {
            'type': 'doughnut',
            'data': {
                'labels': list(register_labels) if register_labels else ['—'],
                'datasets': [
                    {
                        'data': [float(x) for x in register_data] if register_data else [0.0],
                        'backgroundColor': ['#d4a373', '#a6b07f', '#2c6b8a', '#e67e22', '#95a5a6', '#7a7268', '#c9b896', '#5d4e37'],
                        'borderWidth': 0,
                        'hoverOffset': 8,
                    }
                ],
            },
            'options': common_opts,
        },
        'pos_vs_branch_6m': {
            'type': 'bar',
            'data': {
                'labels': labels_6m,
                'datasets': [
                    {'label': 'POS', 'data': pos_6m, 'backgroundColor': 'rgba(212, 163, 115, 0.85)', 'borderRadius': 6},
                    {'label': 'Filial', 'data': br_6m, 'backgroundColor': 'rgba(44, 107, 138, 0.75)', 'borderRadius': 6},
                ],
            },
            'options': {**common_opts, 'scales': {'x': {'grid': {'display': False}}, 'y': {'beginAtZero': True}}},
        },
        'daily_sales_14d': {
            'type': 'line',
            'data': {
                'labels': labels_14d,
                'datasets': [
                    {
                        'label': 'POS',
                        'data': pos_14,
                        'borderColor': 'rgb(212, 163, 115)',
                        'backgroundColor': 'rgba(212, 163, 115, 0.15)',
                        'fill': True,
                        'tension': 0.25,
                    },
                    {
                        'label': 'Filial',
                        'data': br_14,
                        'borderColor': 'rgb(44, 107, 138)',
                        'backgroundColor': 'rgba(44, 107, 138, 0.1)',
                        'fill': True,
                        'tension': 0.25,
                    },
                ],
            },
            'options': {**common_opts, 'scales': {'y': {'beginAtZero': True}}},
        },
        'tx_type_pie': {
            'type': 'pie',
            'data': {
                'labels': tx_type_labels,
                'datasets': [{'data': tx_type_vals, 'backgroundColor': ['#d4a373', '#2c6b8a', '#a6b07f', '#e67e22', '#95a5a6']}],
            },
            'options': common_opts,
        },
        'expense_categories': {
            'type': 'bar',
            'data': {
                'labels': exp_cat_labels,
                'datasets': [{'label': 'UZS', 'data': exp_cat_vals, 'backgroundColor': 'rgba(220, 53, 69, 0.55)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'indexAxis': 'y', 'scales': {'x': {'beginAtZero': True}}},
        },
        'supplier_debt': {
            'type': 'bar',
            'data': {
                'labels': sup_labels,
                'datasets': [{'label': 'Qarz', 'data': sup_vals, 'backgroundColor': 'rgba(243, 156, 18, 0.65)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'indexAxis': 'y', 'scales': {'x': {'beginAtZero': True}}},
        },
        'payment_methods': {
            'type': 'pie',
            'data': {
                'labels': pm_labels,
                'datasets': [{'data': pm_vals, 'backgroundColor': ['#d4a373', '#2c6b8a', '#a6b07f', '#7a7268']}],
            },
            'options': common_opts,
        },
        'top_products': {
            'type': 'bar',
            'data': {
                'labels': prod_labels,
                'datasets': [{'label': 'Daromad', 'data': prod_vals, 'backgroundColor': 'rgba(46, 139, 87, 0.65)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'indexAxis': 'y', 'scales': {'x': {'beginAtZero': True}}},
        },
        'branch_sales_month': {
            'type': 'bar',
            'data': {
                'labels': br_name_labels,
                'datasets': [{'label': 'Savdo', 'data': br_sale_vals, 'backgroundColor': 'rgba(44, 107, 138, 0.7)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'scales': {'y': {'beginAtZero': True}}},
        },
        'journal_daily_14': {
            'type': 'line',
            'data': {
                'labels': je_labels,
                'datasets': [
                    {
                        'label': 'Jurnal yozuvlari',
                        'data': je_counts,
                        'borderColor': 'rgb(90, 90, 120)',
                        'backgroundColor': 'rgba(90, 90, 120, 0.12)',
                        'fill': True,
                        'tension': 0.3,
                    }
                ],
            },
            'options': {**common_opts, 'scales': {'y': {'beginAtZero': True, 'ticks': {'stepSize': 1}}}},
        },
        'gl_activity': {
            'type': 'bar',
            'data': {
                'labels': gl_labels,
                'datasets': [{'label': 'Faollik (D+K)', 'data': gl_vals, 'backgroundColor': 'rgba(123, 104, 238, 0.55)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'indexAxis': 'y', 'scales': {'x': {'beginAtZero': True}}},
        },
        'hourly_pos_today': {
            'type': 'bar',
            'data': {
                'labels': hourly_labels,
                'datasets': [{'label': 'UZS', 'data': hourly_vals, 'backgroundColor': 'rgba(212, 163, 115, 0.8)', 'borderRadius': 4}],
            },
            'options': {**common_opts, 'scales': {'y': {'beginAtZero': True}}},
        },
        'tx_type_counts': {
            'type': 'bar',
            'data': {
                'labels': cnt_labels,
                'datasets': [{'label': 'Soni', 'data': cnt_vals, 'backgroundColor': 'rgba(100, 149, 237, 0.65)', 'borderRadius': 6}],
            },
            'options': {**common_opts, 'scales': {'y': {'beginAtZero': True, 'ticks': {'stepSize': 1}}}},
        },
        'trial_balance_split': {
            'type': 'doughnut',
            'data': {
                'labels': ['Jami debet', 'Jami kredit'],
                'datasets': [{'data': [tb_d, tb_c], 'backgroundColor': ['#5c7cfa', '#f06595']}],
            },
            'options': common_opts,
        },
    }
