from django.db import models
from django.contrib.auth.models import User
from production.models import Product

class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    responsible_person = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BranchManager(models.Model):
    """Filial rahbari - filial uchun alohida login"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='managers')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='branch_manager_profile')
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Ruxsatlar
    can_manage_employees = models.BooleanField(default=True)
    can_manage_sales = models.BooleanField(default=True)
    can_manage_accounting = models.BooleanField(default=True)
    can_manage_production = models.BooleanField(default=True)
    can_manage_warehouse = models.BooleanField(default=True)
    can_manage_recipes = models.BooleanField(default=True)
    can_create_branch = models.BooleanField(default=False, help_text="Yangi filial yarata olishi (faqat superadmin)")

    def __str__(self):
        return f"{self.user.username} - {self.branch.name}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

class BranchInventory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('branch', 'product')

    def __str__(self):
        return f"{self.branch.name} - {self.product.name}: {self.stock}"

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
    ]
    date_sent = models.DateTimeField(auto_now_add=True)
    date_received = models.DateTimeField(null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')

    def __str__(self):
        return f"Transfer to {self.branch.name} on {self.date_sent.strftime('%Y-%m-%d')}"

class TransferItem(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} {self.product.name} in Transfer {self.transfer.id}"

class BranchSale(models.Model):
    date = models.DateField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='sales')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sales for {self.branch.name} on {self.date}"

class BranchSaleItem(models.Model):
    branch_sale = models.ForeignKey(BranchSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} at {self.branch_sale.branch.name}"
