from django.db import models

class RawMaterial(models.fields.CharField):
    # This class shouldn't inherit from CharField
    pass

# Redefining correctly
class RawMaterial(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, help_text="e.g., kg, liter, piece")
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.stock} {self.unit})"

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price")
    
    def __str__(self):
        return self.name

class Recipe(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='recipe')
    batch_size = models.IntegerField(help_text="Quantity produced by this recipe (e.g., 100 loaves)")

    def __str__(self):
        return f"Recipe for {self.product.name}"

class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, help_text="Amount needed for the batch size")

    def __str__(self):
        return f"{self.quantity} {self.raw_material.unit} of {self.raw_material.name} for {self.recipe.product.name}"

class FinishedGoodsInventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} Stock: {self.stock}"

class ProductionLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(help_text="Quantity produced")
    # Using string for baker to avoid circular dependency with hr app right now, or we can import later
    baker_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} {self.product.name} produced on {self.date.strftime('%Y-%m-%d %H:%M')}"
