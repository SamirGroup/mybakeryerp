from django.db import models
from production.models import Product

class Sale(models.fields.CharField):
    pass

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('terminal', 'Terminal'),
        ('electronic', 'Electronic (Click/Payme)'),
    ]
    
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    
    def __str__(self):
        return f"Sale {self.id} on {self.date.strftime('%Y-%m-%d %H:%M')} - {self.total_amount}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Sale {self.sale.id})"

class ReturnLog(models.Model):
    REASON_CHOICES = [
        ('brak', 'Brak (Unusable)'),
        ('unsold', 'Unsold'),
    ]
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Returned {self.quantity} {self.product.name} ({self.get_reason_display()})"
