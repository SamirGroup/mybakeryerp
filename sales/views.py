from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Sale, SaleItem, ReturnLog
from production.models import Product, FinishedGoodsInventory
from accounting.models import CashRegister, Transaction as AccountingTransaction

def sales_dashboard(request):
    products = Product.objects.all()
    finished_goods = FinishedGoodsInventory.objects.all()
    recent_sales = Sale.objects.all().order_by('-date')[:10]
    
    if request.method == 'POST':
        if 'quick_sale' in request.POST:
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity'))
            payment_method = request.POST.get('payment_method')
            
            try:
                with transaction.atomic():
                    product = Product.objects.get(id=product_id)
                    fg = FinishedGoodsInventory.objects.get(product=product)
                    
                    if fg.stock < quantity:
                        raise ValueError(f"Not enough {product.name} in stock (Only {fg.stock} left).")
                    
                    # Deduct from inventory
                    fg.stock -= quantity
                    fg.save()
                    
                    # Create Sale
                    total_price = product.price * quantity
                    sale = Sale.objects.create(total_amount=total_price, payment_method=payment_method)
                    SaleItem.objects.create(sale=sale, product=product, quantity=quantity, price_at_sale=product.price)
                    
                    # Add to Cash Register
                    # Map payment methods to register names
                    register_name = 'Main Cash' if payment_method == 'cash' else 'Terminal'
                    register, _ = CashRegister.objects.get_or_create(name=register_name)
                    register.balance += total_price
                    register.save()
                    
                    # Record transaction
                    AccountingTransaction.objects.create(
                        cash_register=register,
                        amount=total_price,
                        transaction_type='income',
                        description=f"Sale #{sale.id} ({payment_method})"
                    )
                    
                    messages.success(request, f"Sale completed: {quantity} {product.name} for {total_price}.")
            except FinishedGoodsInventory.DoesNotExist:
                messages.error(request, "Product not in inventory.")
            except ValueError as e:
                messages.error(request, str(e))
                
            return redirect('sales_dashboard')
            
        elif 'add_return' in request.POST:
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity'))
            reason = request.POST.get('reason')
            
            try:
                product = Product.objects.get(id=product_id)
                ReturnLog.objects.create(product=product, quantity=quantity, reason=reason)
                messages.warning(request, f"Returned {quantity} {product.name} as {reason}.")
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
                
            return redirect('sales_dashboard')

    context = {
        'products': products,
        'finished_goods': finished_goods,
        'recent_sales': recent_sales,
    }
    return render(request, 'sales.html', context)
