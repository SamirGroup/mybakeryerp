from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RawMaterial(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, help_text="e.g., kg, liter, piece")
    stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.name} ({self.stock} {self.unit})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='recipe')
    batch_size = models.IntegerField(help_text="Quantity produced by this recipe")

    def __str__(self):
        return f"Recipe for {self.product.name}"


class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, help_text="Amount in raw_material's unit")
    quantity_grams = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text="Optional gram equivalent if unit is kg")

    def __str__(self):
        return f"{self.quantity} {self.raw_material.unit} of {self.raw_material.name}"


class ProductDayBalance(models.Model):
    """Kunlik tayyor mahsulot yozuvi: kirish (oldingi kun yopilishi) va chiqish (kun yakuni)."""

    balance_date = models.DateField(db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='day_balances')
    opening_qty = models.IntegerField(default=0, help_text="Kun boshidagi qoldiq (oldingi kun closing yoki carried-forward)")
    closing_qty = models.IntegerField(null=True, blank=True, help_text="Kun yakunidagi fizik qoldiq")
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['balance_date', 'product'], name='uniq_product_day_balance'),
        ]

    def __str__(self):
        return f"{self.balance_date} {self.product.name}"


class FinishedGoodsInventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock = models.IntegerField(default=0)
    produced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} Stock: {self.stock}"


class ProductionLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    batches = models.IntegerField(default=1, help_text="Number of recipe batches")
    baker_name = models.CharField(max_length=255, blank=True, null=True)
    timer_minutes = models.IntegerField(default=0, help_text="Production timer in minutes")
    timer_started_at = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} {self.product.name} on {self.date.strftime('%Y-%m-%d %H:%M')}"
