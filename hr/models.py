from django.db import models

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('vacation', 'On Vacation'),
        ('left', 'Left'),
    ]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100, help_text="e.g., Baker, Seller, Guard")
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Salary fields
    is_piecework = models.BooleanField(default=False, help_text="Checked for Bakers (paid per loaf)")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fixed monthly salary if applicable")
    piecework_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate per piece if piecework")

    def __str__(self):
        return f"{self.name} ({self.position})"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=[('day', 'Day'), ('night', 'Night')], default='day')

    def __str__(self):
        return f"{self.employee.name} on {self.date}"

class AdvancePayment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # the actual deduction from accounting CashRegister will be handled in a signal or view

    def __str__(self):
        return f"Advance of {self.amount} to {self.employee.name} on {self.date}"

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField(help_text="The month this payroll corresponds to (e.g., 2026-04-01 for April)")
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    piecework_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    advance_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Payroll for {self.employee.name} - {self.month.strftime('%Y-%m')}"
