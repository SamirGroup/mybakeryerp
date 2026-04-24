from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction as db_transaction
from decimal import Decimal, InvalidOperation
from .models import CashRegister, ExpenseCategory, Supplier, Transaction as AccTransaction


def accounting_dashboard(request):
    registers = CashRegister.objects.all()
    expense_cats = ExpenseCategory.objects.all()
    suppliers = Supplier.objects.all()
    recent_transactions = AccTransaction.objects.all().order_by('-date')[:20]

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # ── ADD CASH REGISTER ────────────────────────────────────────
        if action == 'add_register':
            name = request.POST.get('name', '').strip()
            balance = request.POST.get('initial_balance', 0) or 0
            if name:
                reg, created = CashRegister.objects.get_or_create(name=name, defaults={'balance': balance})
                if created:
                    messages.success(request, f"Kassa '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' nomli kassa allaqachon mavjud.")
            else:
                messages.error(request, "Kassa nomi majburiy.")

        # ── ADD EXPENSE CATEGORY ─────────────────────────────────────
        elif action == 'add_category':
            name = request.POST.get('name', '').strip()
            if name:
                cat, created = ExpenseCategory.objects.get_or_create(name=name)
                if created:
                    messages.success(request, f"Kategoriya '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' allaqachon mavjud.")
            else:
                messages.error(request, "Kategoriya nomi majburiy.")

        # ── ADD SUPPLIER ─────────────────────────────────────────────
        elif action == 'add_supplier':
            name = request.POST.get('name', '').strip()
            contact = request.POST.get('contact', '').strip()
            if name:
                sup, created = Supplier.objects.get_or_create(name=name, defaults={'contact_info': contact})
                if created:
                    messages.success(request, f"Ta'minotchi '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"'{name}' allaqachon mavjud.")
            else:
                messages.error(request, "Ta'minotchi nomi majburiy.")

        # ── DELETE REGISTER ──────────────────────────────────────────
        elif action == 'delete_register':
            rid = request.POST.get('register_id')
            try:
                CashRegister.objects.get(id=rid).delete()
                messages.success(request, "Kassa o'chirildi.")
            except CashRegister.DoesNotExist:
                messages.error(request, "Kassa topilmadi.")

        # ── DELETE CATEGORY ──────────────────────────────────────────
        elif action == 'delete_category':
            cid = request.POST.get('category_id')
            try:
                ExpenseCategory.objects.get(id=cid).delete()
                messages.success(request, "Kategoriya o'chirildi.")
            except ExpenseCategory.DoesNotExist:
                messages.error(request, "Kategoriya topilmadi.")

        # ── DELETE SUPPLIER ──────────────────────────────────────────
        elif action == 'delete_supplier':
            sid = request.POST.get('supplier_id')
            try:
                Supplier.objects.get(id=sid).delete()
                messages.success(request, "Ta'minotchi o'chirildi.")
            except Supplier.DoesNotExist:
                messages.error(request, "Ta'minotchi topilmadi.")

        # ── RECORD EXPENSE ───────────────────────────────────────────
        elif 'add_expense' in request.POST:
            try:
                amount = Decimal(request.POST.get('amount', '0'))
            except InvalidOperation:
                messages.error(request, "Noto'g'ri summa kiritildi.")
                return redirect('accounting_dashboard')
            register_id = request.POST.get('register')
            category_id = request.POST.get('category')
            description = request.POST.get('description', '')
            try:
                with db_transaction.atomic():
                    reg = CashRegister.objects.get(id=register_id)
                    cat = ExpenseCategory.objects.get(id=category_id)
                    if reg.balance < amount:
                        raise ValueError(f"{reg.name} kassasida yetarli mablag' yo'q. Mavjud: {reg.balance} UZS")
                    reg.balance -= amount
                    reg.save()
                    AccTransaction.objects.create(
                        cash_register=reg, amount=amount,
                        transaction_type='expense',
                        expense_category=cat, description=description
                    )
                    messages.success(request, f"{amount:,.0f} UZS xarajat qayd etildi.")
            except (CashRegister.DoesNotExist, ExpenseCategory.DoesNotExist):
                messages.error(request, "Kassa yoki kategoriya topilmadi.")
            except ValueError as e:
                messages.error(request, str(e))

        # ── TRANSFER FUNDS ───────────────────────────────────────────
        elif 'transfer_funds' in request.POST:
            try:
                amount = Decimal(request.POST.get('amount', '0'))
            except InvalidOperation:
                messages.error(request, "Noto'g'ri summa kiritildi.")
                return redirect('accounting_dashboard')
            from_id = request.POST.get('from_register')
            to_id = request.POST.get('to_register')
            if from_id == to_id:
                messages.error(request, "Bir xil kassaga o'tkazib bo'lmaydi.")
            else:
                try:
                    with db_transaction.atomic():
                        from_reg = CashRegister.objects.get(id=from_id)
                        to_reg = CashRegister.objects.get(id=to_id)
                        if from_reg.balance < amount:
                            raise ValueError(f"{from_reg.name} kassasida yetarli mablag' yo'q. Mavjud: {from_reg.balance} UZS")
                        from_reg.balance -= amount
                        to_reg.balance += amount
                        from_reg.save()
                        to_reg.save()
                        AccTransaction.objects.create(
                            cash_register=from_reg, transfer_to=to_reg,
                            amount=amount, transaction_type='transfer',
                            description=f"{from_reg.name} → {to_reg.name}"
                        )
                        messages.success(request, f"{amount:,.0f} UZS o'tkazildi: {from_reg.name} → {to_reg.name}")
                except CashRegister.DoesNotExist:
                    messages.error(request, "Kassa topilmadi.")
                except ValueError as e:
                    messages.error(request, str(e))

        return redirect('accounting_dashboard')

    context = {
        'registers': registers,
        'expense_cats': expense_cats,
        'suppliers': suppliers,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'accounting.html', context)
