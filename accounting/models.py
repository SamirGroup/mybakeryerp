from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Account(models.Model):
    """Hisoblar rejasi — Chart of Accounts."""

    ACCOUNT_TYPES = [
        ('asset', 'Aktiv'),
        ('liability', 'Majburiyat'),
        ('equity', 'Kapital'),
        ('revenue', 'Daromad'),
        ('expense', 'Xarajat'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"


class CashRegister(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Main, Terminal, Expense")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    gl_account = models.OneToOneField(
        Account,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cash_register',
    )
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE,
        null=True, blank=True, related_name='cash_registers',
        verbose_name="Filial (bo'sh = asosiy ofis)"
    )

    def __str__(self):
        prefix = f"[{self.branch.name}] " if self.branch else ""
        return f"{prefix}{self.name} — {self.balance}"


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Utilities, Raw Materials, Household")

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    debt = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} (Qarz: {self.debt})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('supplier_payment', 'Supplier Payment'),
    ]
    date = models.DateTimeField(auto_now_add=True)
    cash_register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transactions'
    )
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE,
        null=True, blank=True, related_name='transactions',
        verbose_name="Filial (bo'sh = asosiy ofis)"
    )

    expense_category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_to = models.ForeignKey(
        CashRegister, on_delete=models.SET_NULL, related_name='incoming_transfers', null=True, blank=True
    )

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} @ {self.date:%Y-%m-%d}"


class JournalEntry(models.Model):
    """Jurnal sarlavhasi — ikki tomonlama yozuvlar to‘plami."""

    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('posted', 'Tasdiqlangan'),
    ]
    SOURCE_CHOICES = [
        ('manual', 'Qo‘lda jurnal'),
        ('cash', 'Kassa operatsiyasi'),
        ('sales', 'POS savdo'),
        ('branch', 'Filial savdo'),
        ('system', 'Tizim'),
    ]

    entry_date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=64, blank=True)
    memo = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='posted')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='journal_entry',
    )

    class Meta:
        ordering = ['-entry_date', '-id']

    def __str__(self):
        return f"JE #{self.id} {self.entry_date:%Y-%m-%d} {self.reference or ''}"

    def total_debit(self):
        return self.lines.aggregate(t=Sum('debit'))['t'] or 0

    def total_credit(self):
        return self.lines.aggregate(t=Sum('credit'))['t'] or 0


class JournalLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_lines')
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.account.code} D{self.debit} C{self.credit}"

    def clean(self):
        super().clean()
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("Bir qatorda faqat debet yoki faqat kredit bo‘lishi kerak.")
        if self.debit < 0 or self.credit < 0:
            raise ValidationError("Manfiy summalar ruxsat etilmaydi.")
        if self.debit == 0 and self.credit == 0:
            raise ValidationError("Debet yoki kiritdan biri musbat bo‘lishi kerak.")
