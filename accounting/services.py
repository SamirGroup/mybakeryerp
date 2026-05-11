"""
Buxgalteriya yadrosi: hisoblar rejasi, jurnal yozuvlari va kassa operatsiyalari integratsiyasi.
"""
from decimal import Decimal, InvalidOperation
from django.db import transaction as db_transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Account,
    CashRegister,
    ExpenseCategory,
    JournalEntry,
    JournalLine,
    Supplier,
    Transaction,
)

# Boshqaruv hisoblari kodlari
CODE_AP = '2100'
CODE_REV = '4100'
CODE_EXP = '5000'
CODE_PURCHASE = '5010'


def _d(x) -> Decimal:
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))


def ensure_control_accounts():
    """Asosiy sinov hisoblarini yaratadi (bir marta)."""
    defaults = [
        (CODE_AP, 'Ta\'minotchilar qarzi (kreditorlik)', 'liability'),
        (CODE_REV, 'Savdo daromadi', 'revenue'),
        (CODE_EXP, 'Umumiy operatsion xarajat', 'expense'),
        (CODE_PURCHASE, 'Xaridlar (qarzga)', 'expense'),
    ]
    for code, name, atype in defaults:
        Account.objects.get_or_create(
            code=code,
            defaults={'name': name, 'account_type': atype},
        )


def ensure_register_gl(register: CashRegister) -> Account:
    """Har bir kassa uchun aktiv hisob (11xxx)."""
    ensure_control_accounts()
    if register.gl_account_id:
        return register.gl_account
    code = f'11{register.id:03d}'
    acc, _ = Account.objects.get_or_create(
        code=code,
        defaults={
            'name': f"Kassa: {register.name}",
            'account_type': 'asset',
        },
    )
    register.gl_account = acc
    register.save(update_fields=['gl_account'])
    return acc


def _validate_balance(lines: list[tuple[Account, Decimal, Decimal]]):
    td = sum((d for _, d, _ in lines), Decimal('0'))
    tc = sum((c for _, _, c in lines), Decimal('0'))
    if td != tc:
        raise ValueError(f"Jurnal muvozanatsiz: Debet {td} ≠ Kredit {tc}")


@db_transaction.atomic
def record_income(register: CashRegister, amount, user, description: str = ''):
    amount = _d(amount)
    if amount <= 0:
        raise ValueError('Summa musbat bo‘lishi kerak.')
    reg_acc = ensure_register_gl(register)
    rev = Account.objects.get(code=CODE_REV)
    tx = Transaction.objects.create(
        cash_register=register,
        amount=amount,
        transaction_type='income',
        description=description or 'Naqd tushum',
    )
    register.balance += amount
    register.save(update_fields=['balance'])
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=f'INC-{tx.id}',
        memo=description or 'Kassaga tushum',
        source='cash',
        created_by=user,
        transaction=tx,
    )
    lines = [(reg_acc, amount, Decimal('0')), (rev, Decimal('0'), amount)]
    _validate_balance(lines)
    for acc, d, c in lines:
        JournalLine.objects.create(entry=je, account=acc, debit=d, credit=c)
    return tx


@db_transaction.atomic
def record_expense(register: CashRegister, amount, category: ExpenseCategory, user, description: str = ''):
    amount = _d(amount)
    if amount <= 0:
        raise ValueError('Summa musbat bo‘lishi kerak.')
    reg_acc = ensure_register_gl(register)
    exp = Account.objects.get(code=CODE_EXP)
    if register.balance < amount:
        raise ValueError(f"{register.name} kassasida yetarli mablag‘ yo‘q. Qoldiq: {register.balance}")
    tx = Transaction.objects.create(
        cash_register=register,
        amount=amount,
        transaction_type='expense',
        expense_category=category,
        description=description or category.name,
    )
    register.balance -= amount
    register.save(update_fields=['balance'])
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=f'EXP-{tx.id}',
        memo=f"{category.name}: {description}".strip(),
        source='cash',
        created_by=user,
        transaction=tx,
    )
    lines = [(exp, amount, Decimal('0')), (reg_acc, Decimal('0'), amount)]
    _validate_balance(lines)
    for acc, d, c in lines:
        JournalLine.objects.create(entry=je, account=acc, debit=d, credit=c, description=description[:500])
    return tx


@db_transaction.atomic
def record_transfer(from_reg: CashRegister, to_reg: CashRegister, amount, user, description: str = ''):
    amount = _d(amount)
    if amount <= 0:
        raise ValueError('Summa musbat bo‘lishi kerak.')
    if from_reg.id == to_reg.id:
        raise ValueError('Bir xil kassa tanlangan.')
    from_acc = ensure_register_gl(from_reg)
    to_acc = ensure_register_gl(to_reg)
    if from_reg.balance < amount:
        raise ValueError(f"{from_reg.name} kassasida yetarli mablag‘ yo‘q.")
    tx = Transaction.objects.create(
        cash_register=from_reg,
        amount=amount,
        transaction_type='transfer',
        transfer_to=to_reg,
        description=description or f"{from_reg.name} → {to_reg.name}",
    )
    from_reg.balance -= amount
    to_reg.balance += amount
    from_reg.save(update_fields=['balance'])
    to_reg.save(update_fields=['balance'])
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=f'TRF-{tx.id}',
        memo=description or f"O‘tkazma: {from_reg.name} → {to_reg.name}",
        source='cash',
        created_by=user,
        transaction=tx,
    )
    lines = [(to_acc, amount, Decimal('0')), (from_acc, Decimal('0'), amount)]
    _validate_balance(lines)
    for acc, d, c in lines:
        JournalLine.objects.create(entry=je, account=acc, debit=d, credit=c)
    return tx


@db_transaction.atomic
def record_supplier_payment(register: CashRegister, supplier: Supplier, amount, user, description: str = ''):
    amount = _d(amount)
    if amount <= 0:
        raise ValueError('Summa musbat bo‘lishi kerak.')
    reg_acc = ensure_register_gl(register)
    ap = Account.objects.get(code=CODE_AP)
    if register.balance < amount:
        raise ValueError(f"{register.name} kassasida yetarli mablag‘ yo‘q.")
    if supplier.debt < amount:
        raise ValueError('To‘lov summasi ta\'minotchi qarzidan oshmasligi kerak.')
    tx = Transaction.objects.create(
        cash_register=register,
        amount=amount,
        transaction_type='supplier_payment',
        supplier=supplier,
        description=description or f"To‘lov: {supplier.name}",
    )
    register.balance -= amount
    supplier.debt -= amount
    register.save(update_fields=['balance'])
    supplier.save(update_fields=['debt'])
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=f'AP-{tx.id}',
        memo=description or f"Ta\'minotchi: {supplier.name}",
        source='cash',
        created_by=user,
        transaction=tx,
    )
    lines = [(ap, amount, Decimal('0')), (reg_acc, Decimal('0'), amount)]
    _validate_balance(lines)
    for acc, d, c in lines:
        JournalLine.objects.create(entry=je, account=acc, debit=d, credit=c)
    return tx


@db_transaction.atomic
def record_supplier_debt_increase(supplier: Supplier, amount, user, description: str = ''):
    """Qarzga xarid: Dr Xarid / Cr Kreditorlik (naqd harakatsiz)."""
    amount = _d(amount)
    if amount <= 0:
        raise ValueError('Summa musbat bo‘lishi kerak.')
    ensure_control_accounts()
    pur = Account.objects.get(code=CODE_PURCHASE)
    ap = Account.objects.get(code=CODE_AP)
    supplier.debt += amount
    supplier.save(update_fields=['debt'])
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=f'ACR-{supplier.id}-{timezone.now().timestamp():.0f}',
        memo=description or f"Qarzga xarid: {supplier.name}",
        source='cash',
        created_by=user,
    )
    lines = [(pur, amount, Decimal('0')), (ap, Decimal('0'), amount)]
    _validate_balance(lines)
    for acc, d, c in lines:
        JournalLine.objects.create(entry=je, account=acc, debit=d, credit=c)
    return je


@db_transaction.atomic
def post_manual_journal(user, memo: str, reference: str, rows: list[dict]):
    """
    rows: [{'account_id': int, 'debit': '0', 'credit': '0', 'description': ''}, ...]
    """
    ensure_control_accounts()
    parsed = []
    for r in rows:
        aid = r.get('account_id')
        if not aid:
            continue
        try:
            d = _d(r.get('debit') or 0)
            c = _d(r.get('credit') or 0)
        except (InvalidOperation, TypeError):
            raise ValueError('Noto‘g‘ri summa.')
        if d < 0 or c < 0:
            raise ValueError('Manfiy summalar ruxsat etilmaydi.')
        if d > 0 and c > 0:
            raise ValueError('Bir qatorda faqat debet yoki kredit.')
        if d == 0 and c == 0:
            continue
        acc = Account.objects.get(pk=int(aid))
        parsed.append(
            {
                'account': acc,
                'debit': d,
                'credit': c,
                'description': (r.get('description') or '')[:500],
            }
        )
    if len(parsed) < 2:
        raise ValueError('Kamida ikkita to‘ldirilgan qator kerak.')
    td = sum(x['debit'] for x in parsed)
    tc = sum(x['credit'] for x in parsed)
    if td != tc:
        raise ValueError(f"Debet ({td}) va kredit ({tc}) teng emas.")
    je = JournalEntry.objects.create(
        entry_date=timezone.now(),
        reference=reference[:64],
        memo=memo,
        source='manual',
        created_by=user,
    )
    for x in parsed:
        JournalLine.objects.create(
            entry=je,
            account=x['account'],
            debit=x['debit'],
            credit=x['credit'],
            description=x['description'],
        )
    return je


def cash_register_rows_from_registers(registers):
    """
    Kassa UI uchun ro‘yxat: id, name, balance, gl_code.
    GL bog‘langan kassalar uchun balans jurnal qatorlaridan (aktiv: debet − kredit);
    yozuv bo‘lmasa yoki GL yo‘q bo‘lsa — CashRegister.balance.
    """
    registers = list(registers)
    account_ids = [r.gl_account_id for r in registers if r.gl_account_id]
    sums_by_account = {}
    if account_ids:
        ag = (
            JournalLine.objects.filter(account_id__in=account_ids)
            .values('account_id')
            .annotate(dt=Sum('debit'), ct=Sum('credit'))
        )
        for row in ag:
            d = row['dt'] or Decimal('0')
            c = row['ct'] or Decimal('0')
            sums_by_account[row['account_id']] = d - c
    out = []
    for r in registers:
        if r.gl_account_id:
            if r.gl_account_id in sums_by_account:
                bal = sums_by_account[r.gl_account_id]
            else:
                bal = r.balance
        else:
            bal = r.balance
        out.append(
            {
                'id': r.id,
                'name': r.name,
                'balance': bal,
                'gl_code': r.gl_account.code if r.gl_account_id else '',
            }
        )
    return out


def trial_balance():
    """Jurnal qatorlari bo‘yicha sinov balansi."""
    qs = (
        JournalLine.objects.values('account__code', 'account__name', 'account__account_type')
        .annotate(debit_total=Sum('debit'), credit_total=Sum('credit'))
        .order_by('account__code')
    )
    rows = []
    for r in qs:
        rows.append(
            {
                'code': r['account__code'],
                'name': r['account__name'],
                'type': r['account__account_type'],
                'debit': r['debit_total'] or Decimal('0'),
                'credit': r['credit_total'] or Decimal('0'),
            }
        )
    return rows


def backfill_gl_for_existing_registers():
    """Migratsiya yoki admin uchun: mavjud kassalarga GL hisob bog‘lash."""
    ensure_control_accounts()
    for reg in CashRegister.objects.filter(gl_account__isnull=True):
        ensure_register_gl(reg)
