from django.db import models
from django.contrib.auth.models import User
from production.models import Product


class ShiftDailyAllocation(models.Model):
    """Smenaga kunlik mahsulot ajratish (qoldiqni smena bo'yicha kuzatish)."""

    date = models.DateField(db_index=True)
    shift_name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shift_allocations')
    allocated_qty = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'shift_name', 'product'],
                name='uniq_sales_shift_day_product_alloc',
            )
        ]

    def __str__(self):
        return f"{self.shift_name} {self.date}: {self.product.name} → {self.allocated_qty}"


class ShiftClosure(models.Model):
    """Smena yopilishi (kunlik yakuniy qayd)."""

    date = models.DateField(db_index=True)
    shift_name = models.CharField(max_length=100)
    closed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='shift_closures')
    closed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'shift_name'],
                name='uniq_sales_shift_day_closure',
            )
        ]

    def __str__(self):
        return f"{self.shift_name} yopildi {self.date}"


class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Naqd'),
        ('terminal', 'Terminal'),
        ('electronic', 'Click/Payme'),
    ]
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    seller = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    shift_name = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"Sale #{self.id} — {self.total_amount} UZS"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ReturnLog(models.Model):
    REASON_CHOICES = [
        ('brak', 'Brak'),
        ('unsold', 'Sotilmagan'),
    ]
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Return {self.quantity} {self.product.name}"
