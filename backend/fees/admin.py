from django.contrib import admin
from fees.models import FeeCategory, FeeStructure, StudentInvoice, Payment, PaymentReceipt


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "college"]
    search_fields = ["name", "code"]


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "semester_number", "academic_year", "total_amount", "college"]
    list_filter = ["academic_year", "course", "college"]


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "student", "final_amount", "paid_amount", "balance_due", "status", "due_date", "college"]
    list_filter = ["status", "due_date", "college"]
    search_fields = ["invoice_number", "student__roll_number", "student__user__first_name", "student__user__last_name"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["transaction_reference", "invoice", "student", "amount", "payment_method", "status", "paid_at", "college"]
    list_filter = ["payment_method", "status", "college"]
    search_fields = ["transaction_reference", "invoice__invoice_number", "student__roll_number"]


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "invoice", "student", "issued_at", "college"]
    search_fields = ["receipt_number", "invoice__invoice_number", "student__roll_number"]
