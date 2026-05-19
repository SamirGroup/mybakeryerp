from django.contrib import admin
from .models import Employee, Position, Shift, DailyReport, Attendance, AdvancePayment, Payroll, EmployeePhoto, FaceIDLog


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'phone', 'shift', 'status', 'face_id_enrolled', 'is_piecework', 'branch']
    list_filter = ['status', 'position', 'face_id_enrolled', 'branch']
    search_fields = ['name', 'phone']
    list_select_related = ['shift', 'branch']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time']


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'shift', 'was_present', 'units_produced', 'units_from_sales']
    list_filter = ['was_present', 'date']
    search_fields = ['employee__name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'check_in_method', 'late_minutes']
    list_filter = ['check_in_method', 'check_out_method', 'date']
    search_fields = ['employee__name']


@admin.register(EmployeePhoto)
class EmployeePhotoAdmin(admin.ModelAdmin):
    list_display = ['employee', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary']


@admin.register(FaceIDLog)
class FaceIDLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'timestamp', 'action', 'confidence', 'is_late', 'late_minutes']
    list_filter = ['action', 'is_late', 'timestamp']
    search_fields = ['employee__name']


@admin.register(AdvancePayment)
class AdvancePaymentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'amount']
    list_filter = ['date']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'base_pay', 'piecework_pay', 'net_paid']
    list_filter = ['month']
