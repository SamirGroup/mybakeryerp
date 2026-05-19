from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Shift(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 1-smena, 2-smena")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M}–{self.end_time:%H:%M})"


class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('vacation', 'On Vacation'),
        ('left', 'Left'),
    ]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    shift = models.ForeignKey(Shift, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    photo = models.ImageField(upload_to='employees/', null=True, blank=True)
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL, related_name='employees', help_text="Filial rahbari uchun - faqat o'z filialiga ruxsat")

    is_piecework = models.BooleanField(default=False)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    piecework_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Rate per unit produced")
    daily_target = models.IntegerField(default=0, help_text="Daily production target (nagruzka)")
    user_account = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employee_profile',
        help_text="Sotuv panelidagi foydalanuvchi bilan bog'lash (ishbay avtomatik yozuvlari uchun)",
    )

    # Face ID uchun
    face_id_enrolled = models.BooleanField(default=False, help_text="Face ID tizimiga ulangan")
    face_id_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=85.0, help_text="Face ID tanishish ishonchliligi (%)")

    def __str__(self):
        return f"{self.name} ({self.position})"


class DailyReport(models.Model):
    ABSENCE_REASON_CHOICES = [
        ('', '—'),
        ('sick', 'Kasal'),
        ('personal', 'Shaxsiy masala'),
        ('approved', 'Sababli (tasdiqlangan)'),
        ('no_reason', 'Sababsiz'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_reports')
    date = models.DateField()
    shift = models.ForeignKey(Shift, null=True, blank=True, on_delete=models.SET_NULL)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    units_produced = models.IntegerField(default=0, help_text="Qo'lda kiritilgan nagruzka / ishlab chiqarish")
    units_from_sales = models.IntegerField(
        default=0,
        help_text="Sotuvdan avtomatik yozilgan donalar (bog'langan sotuvchi hisobi bilan)",
    )
    notes = models.TextField(blank=True)
    hours_expected = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('8'))
    hours_present = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hours_absent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Kelmagan vaqt")
    hours_left_early = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Erta ketgan vaqt")
    was_present = models.BooleanField(default=True, help_text="False bo'lsa — kelmagan kun")
    absence_reason = models.CharField(
        max_length=20, choices=ABSENCE_REASON_CHOICES, blank=True, default='',
        help_text="Kelmagan sababi"
    )

    class Meta:
        unique_together = ('employee', 'date', 'shift')

    def hours_worked(self):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            ci = datetime.combine(date.today(), self.check_in)
            co = datetime.combine(date.today(), self.check_out)
            diff = (co - ci).total_seconds() / 3600
            return round(diff, 2)
        return 0

    @property
    def piecework_units_total(self):
        return int(self.units_produced or 0) + int(self.units_from_sales or 0)

    @property
    def estimated_piecework_earn(self):
        rate = self.employee.piecework_rate or Decimal('0')
        return Decimal(self.piecework_units_total) * rate

    def __str__(self):
        return f"{self.employee.name} — {self.date}"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    shift = models.CharField(max_length=10, choices=[('day', 'Day'), ('night', 'Night')], default='day')

    # Face ID va avtomatik kuzatuv uchun
    check_in_method = models.CharField(max_length=20, choices=[
        ('face_id', 'Face ID'),
        ('manual', 'Qo\'lda'),
        ('card', 'Karta'),
    ], default='manual')
    check_out_method = models.CharField(max_length=20, choices=[
        ('face_id', 'Face ID'),
        ('manual', 'Qo\'lda'),
        ('card', 'Karta'),
    ], default='manual')
    late_minutes = models.IntegerField(default=0, help_text="Kechikish (daqiqalar)")
    expected_check_in = models.TimeField(null=True, blank=True, help_text="Kutilgan kirish vaqti")
    face_id_snapshot = models.ImageField(upload_to='face_id_snapshots/', null=True, blank=True, help_text="Face ID tasviri")

    def __str__(self):
        return f"{self.employee.name} on {self.date}"


class AdvancePayment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='advances')
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Advance {self.amount} to {self.employee.name}"


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    piecework_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Payroll {self.employee.name} — {self.month:%Y-%m}"


class EmployeePhoto(models.Model):
    """Xodimning bir nechta rasmi - Face ID uchun"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='employee_photos/')
    is_primary = models.BooleanField(default=False, help_text="Asosiy rasm Face ID uchun")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - Photo {self.id}"


class FaceIDLog(models.Model):
    """Face ID orqali kirish/chiqish loglari"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='face_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[
        ('check_in', 'Kirish'),
        ('check_out', 'Chiqish'),
        ('failed', "Noto'g'ri tanish"),
    ])
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Tanishish ishonchliligi")
    snapshot = models.ImageField(upload_to='face_logs/', null=True, blank=True)
    is_late = models.BooleanField(default=False)
    late_minutes = models.IntegerField(default=0)
    shift_start_time = models.TimeField(null=True, blank=True, help_text="Smena boshlanish vaqti")

    def __str__(self):
        return f"{self.employee.name} - {self.action} at {self.timestamp}"
