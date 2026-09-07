from django.contrib import admin
from payroll.models import SalaryStructure, Payslip


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ["faculty", "basic_salary", "gross_salary", "net_salary", "college"]
    search_fields = ["faculty__faculty_number", "faculty__user__first_name", "faculty__user__last_name"]


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ["payslip_number", "faculty", "month", "year", "gross_salary", "net_salary", "status", "payment_date", "college"]
    list_filter = ["month", "year", "status", "college"]
    search_fields = ["payslip_number", "faculty__faculty_number", "faculty__user__first_name", "faculty__user__last_name"]
