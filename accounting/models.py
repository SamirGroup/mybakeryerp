from django.db import models

class CashRegister(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Main, Terminal, Expense")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} - {self.balance}"

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Utilities, Raw Materials, Household")

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    debt = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} (Debt: {self.debt})"

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
    
    # Optional fields depending on transaction type
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_to = models.ForeignKey(CashRegister, on_delete=models.SET_NULL, related_name='incoming_transfers', null=True, blank=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.date.strftime('%Y-%m-%d')}"
