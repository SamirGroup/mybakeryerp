from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import RawMaterial, Product, Recipe, RecipeItem, ProductionLog, FinishedGoodsInventory


def production_dashboard(request):
    raw_materials = RawMaterial.objects.all()
    finished_goods = FinishedGoodsInventory.objects.all()
    recent_logs = ProductionLog.objects.all().order_by('-date')[:10]
    products = Product.objects.all()

    if request.method == 'POST':
        if 'add_production' in request.POST:
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity'))
            baker_name = request.POST.get('baker_name', 'System')

            product = Product.objects.get(id=product_id)
            try:
                recipe = product.recipe
                batches = quantity / recipe.batch_size
                with transaction.atomic():
                    for item in recipe.items.all():
                        required_qty = float(item.quantity) * batches
                        if float(item.raw_material.stock) < required_qty:
                            raise ValueError(f"Not enough {item.raw_material.name}")
                        item.raw_material.stock = float(item.raw_material.stock) - required_qty
                        item.raw_material.save()

                    ProductionLog.objects.create(product=product, quantity=quantity, baker_name=baker_name)

                    fg, created = FinishedGoodsInventory.objects.get_or_create(product=product)
                    fg.stock += quantity
                    fg.save()

                    messages.success(request, f"Successfully logged {quantity} {product.name}.")
            except Recipe.DoesNotExist:
                messages.error(request, f"No recipe defined for {product.name}.")
            except ValueError as e:
                messages.error(request, str(e))

            return redirect('production_dashboard')

    context = {
        'raw_materials': raw_materials,
        'finished_goods': finished_goods,
        'recent_logs': recent_logs,
        'products': products,
    }
    return render(request, 'production.html', context)


def manage_products(request):
    """Product, Raw Material and Recipe Management page"""
    products = Product.objects.all()
    raw_materials = RawMaterial.objects.all()
    recipes = Recipe.objects.all().select_related('product').prefetch_related('items__raw_material')

    if request.method == 'POST':
        action = request.POST.get('action')

        # ── ADD PRODUCT ───────────────────────────────────────────────
        if action == 'add_product':
            name = request.POST.get('name', '').strip()
            price = request.POST.get('price')
            if name and price:
                product, created = Product.objects.get_or_create(name=name, defaults={'price': price})
                if created:
                    FinishedGoodsInventory.objects.create(product=product, stock=0)
                    messages.success(request, f"Mahsulot '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' mahsuloti allaqachon mavjud.")
            else:
                messages.error(request, "Mahsulot nomi va narxi majburiy.")

        # ── ADD RAW MATERIAL ──────────────────────────────────────────
        elif action == 'add_material':
            name = request.POST.get('name', '').strip()
            unit = request.POST.get('unit', '').strip()
            stock = request.POST.get('stock', 0)
            if name and unit:
                mat, created = RawMaterial.objects.get_or_create(
                    name=name, defaults={'unit': unit, 'stock': stock}
                )
                if created:
                    messages.success(request, f"Xom ashyo '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' allaqachon mavjud.")
            else:
                messages.error(request, "Xom ashyo nomi va o'lchov birligi majburiy.")

        # ── ADD / UPDATE RECIPE ───────────────────────────────────────
        elif action == 'add_recipe':
            product_id = request.POST.get('recipe_product')
            batch_size = request.POST.get('batch_size')
            ingredient_ids = request.POST.getlist('ingredient_id')
            ingredient_qtys = request.POST.getlist('ingredient_qty')

            if product_id and batch_size:
                try:
                    with transaction.atomic():
                        product = Product.objects.get(id=product_id)
                        recipe, _ = Recipe.objects.get_or_create(product=product, defaults={'batch_size': batch_size})
                        recipe.batch_size = batch_size
                        recipe.save()

                        # Clear old items and rebuild
                        recipe.items.all().delete()
                        for mat_id, qty in zip(ingredient_ids, ingredient_qtys):
                            if mat_id and qty:
                                raw_mat = RawMaterial.objects.get(id=mat_id)
                                RecipeItem.objects.create(recipe=recipe, raw_material=raw_mat, quantity=qty)

                        messages.success(request, f"'{product.name}' uchun retsept saqlandi.")
                except Product.DoesNotExist:
                    messages.error(request, "Mahsulot topilmadi.")
            else:
                messages.error(request, "Mahsulot va partiya hajmi majburiy.")

        # ── DELETE PRODUCT ────────────────────────────────────────────
        elif action == 'delete_product':
            pid = request.POST.get('product_id')
            try:
                p = Product.objects.get(id=pid)
                p.delete()
                messages.success(request, "Mahsulot o'chirildi.")
            except Product.DoesNotExist:
                messages.error(request, "Mahsulot topilmadi.")

        # ── DELETE RAW MATERIAL ───────────────────────────────────────
        elif action == 'delete_material':
            mid = request.POST.get('material_id')
            try:
                m = RawMaterial.objects.get(id=mid)
                m.delete()
                messages.success(request, "Xom ashyo o'chirildi.")
            except RawMaterial.DoesNotExist:
                messages.error(request, "Xom ashyo topilmadi.")

        # ── RECEIVE RAW MATERIAL (Warehouse intake) ───────────────────
        elif action == 'receive_material':
            mid = request.POST.get('material_id')
            qty = request.POST.get('qty')
            try:
                m = RawMaterial.objects.get(id=mid)
                m.stock += float(qty)
                m.save()
                messages.success(request, f"{m.name}: {qty} {m.unit} qabul qilindi.")
            except RawMaterial.DoesNotExist:
                messages.error(request, "Xom ashyo topilmadi.")

        return redirect('manage_products')

    context = {
        'products': products,
        'raw_materials': raw_materials,
        'recipes': recipes,
    }
    return render(request, 'manage_products.html', context)
