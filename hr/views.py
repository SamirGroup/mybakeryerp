from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Employee, AdvancePayment


def hr_dashboard(request):
    employees = Employee.objects.all()
    active_employees = employees.filter(status='active')
    advances = AdvancePayment.objects.all().order_by('-date')[:15]

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # ── ADD EMPLOYEE ─────────────────────────────────────────────
        if action == 'add_employee':
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            position = request.POST.get('position', '').strip()
            date_joined = request.POST.get('date_joined', '')
            is_piecework = request.POST.get('is_piecework') == 'on'
            base_salary = request.POST.get('base_salary', 0) or 0
            piecework_rate = request.POST.get('piecework_rate', 0) or 0

            if name and position and date_joined:
                emp, created = Employee.objects.get_or_create(
                    name=name, phone=phone,
                    defaults={
                        'position': position,
                        'date_joined': date_joined,
                        'is_piecework': is_piecework,
                        'base_salary': base_salary,
                        'piecework_rate': piecework_rate,
                        'status': 'active',
                    }
                )
                if created:
                    messages.success(request, f"Xodim '{name}' qo'shildi.")
                else:
                    messages.warning(request, f"Bu xodim allaqachon mavjud.")
            else:
                messages.error(request, "Ism, lavozim va qo'shilgan sana majburiy.")

        # ── CHANGE EMPLOYEE STATUS ───────────────────────────────────
        elif action == 'change_status':
            eid = request.POST.get('employee_id')
            new_status = request.POST.get('new_status')
            try:
                emp = Employee.objects.get(id=eid)
                emp.status = new_status
                emp.save()
                messages.success(request, f"{emp.name} holati o'zgartirildi.")
            except Employee.DoesNotExist:
                messages.error(request, "Xodim topilmadi.")

        # ── DELETE EMPLOYEE ──────────────────────────────────────────
        elif action == 'delete_employee':
            eid = request.POST.get('employee_id')
            try:
                emp = Employee.objects.get(id=eid)
                emp.delete()
                messages.success(request, "Xodim o'chirildi.")
            except Employee.DoesNotExist:
                messages.error(request, "Xodim topilmadi.")

        # ── GIVE ADVANCE ─────────────────────────────────────────────
        elif 'give_advance' in request.POST:
            emp_id = request.POST.get('employee')
            amount = request.POST.get('amount')
            try:
                emp = Employee.objects.get(id=emp_id)
                AdvancePayment.objects.create(employee=emp, amount=amount)
                messages.success(request, f"{emp.name} ga {amount} UZS avans berildi.")
            except Employee.DoesNotExist:
                messages.error(request, "Xodim topilmadi.")

        return redirect('hr_dashboard')

    context = {
        'employees': employees,
        'active_employees': active_employees,
        'advances': advances,
        'today': timezone.localdate(),
    }
    return render(request, 'hr.html', context)
