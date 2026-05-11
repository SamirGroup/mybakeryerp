import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery_erp.settings')
django.setup()

from sales.models import Sale, SaleItem
from production.models import Product, FinishedGoodsInventory
from accounting.models import CashRegister

print("Sale count:", Sale.objects.count())
print("SaleItem count:", SaleItem.objects.count())
print("Product count:", Product.objects.count())
print("FinishedGoodsInventory count:", FinishedGoodsInventory.objects.count())
print("All models accessible!")
