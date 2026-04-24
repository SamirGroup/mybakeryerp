from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Branch, Transfer, TransferItem, BranchInventory
from production.models import Product, FinishedGoodsInventory


def branches_dashboard(request):
    branches = Branch.objects.all()
    products = Product.objects.all()
    transfers = Transfer.objects.all().order_by('-date_sent')[:20]

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # ── CREATE BRANCH ─────────────────────────────────────────────
        if action == 'add_branch':
            name = request.POST.get('name', '').strip()
            address = request.POST.get('address', '').strip()
            responsible = request.POST.get('responsible_person', '').strip()
            if name:
                branch, created = Branch.objects.get_or_create(name=name, defaults={
                    'address': address,
                    'responsible_person': responsible,
                })
                if created:
                    messages.success(request, f"Filial '{name}' muvaffaqiyatli qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' nomli filial allaqachon mavjud.")
            else:
                messages.error(request, "Filial nomi majburiy.")
            return redirect('branches_dashboard')

        # ── DELETE BRANCH ─────────────────────────────────────────────
        elif action == 'delete_branch':
            bid = request.POST.get('branch_id')
            try:
                b = Branch.objects.get(id=bid)
                b.delete()
                messages.success(request, "Filial o'chirildi.")
            except Branch.DoesNotExist:
                messages.error(request, "Filial topilmadi.")
            return redirect('branches_dashboard')

        # ── CREATE TRANSFER (Nakladnaya) ───────────────────────────────
        elif 'create_transfer' in request.POST:
            branch_id = request.POST.get('branch')
            product_id = request.POST.get('product')
            quantity = int(request.POST.get('quantity', 0))

            try:
                with transaction.atomic():
                    branch = Branch.objects.get(id=branch_id)
                    product = Product.objects.get(id=product_id)
                    fg = FinishedGoodsInventory.objects.get(product=product)

                    if fg.stock < quantity:
                        raise ValueError(f"Omborda {product.name} yetarli emas. Mavjud: {fg.stock}")

                    fg.stock -= quantity
                    fg.save()

                    transfer = Transfer.objects.create(branch=branch)
                    TransferItem.objects.create(transfer=transfer, product=product, quantity=quantity)

                    messages.success(request, f"{quantity} {product.name} → {branch.name} ga yuborildi.")
            except (Branch.DoesNotExist, Product.DoesNotExist):
                messages.error(request, "Filial yoki mahsulot topilmadi.")
            except FinishedGoodsInventory.DoesNotExist:
                messages.error(request, "Bu mahsulot omborida yo'q.")
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('branches_dashboard')

        # ── RECEIVE TRANSFER ───────────────────────────────────────────
        elif 'receive_transfer' in request.POST:
            transfer_id = request.POST.get('transfer_id')
            try:
                with transaction.atomic():
                    transfer = Transfer.objects.get(id=transfer_id)
                    transfer.status = 'received'
                    transfer.date_received = timezone.now()
                    transfer.save()

                    for item in transfer.items.all():
                        inv, _ = BranchInventory.objects.get_or_create(
                            branch=transfer.branch,
                            product=item.product,
                            defaults={'stock': 0}
                        )
                        inv.stock += item.quantity
                        inv.save()

                    messages.success(request, f"Transfer #{transfer.id} qabul qilindi.")
            except Transfer.DoesNotExist:
                messages.error(request, "Transfer topilmadi.")
            return redirect('branches_dashboard')

    context = {
        'branches': branches,
        'products': products,
        'transfers': transfers,
    }
    return render(request, 'branches.html', context)
