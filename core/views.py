from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from sales.models import Sale
from production.models import ProductionLog
from accounting.models import CashRegister, Supplier
from hr.models import Employee

def dashboard(request):
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Mock data for now, since db might be empty
    context = {
        'today_production': 0,
        'today_sales': 0,
        'today_revenue': 0,
        'yesterday_production': 0,
        'yesterday_revenue': 0,
        'debtors': 0,
        'creditors': sum(s.debt for s in Supplier.objects.all()) or 0,
        'cash_balances': sum(c.balance for c in CashRegister.objects.all()) or 0,
        'employees_on_shift': Employee.objects.filter(status='active').count(), # simplification for now
    }
    
    return render(request, 'dashboard.html', context)
