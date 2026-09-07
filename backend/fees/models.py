from decimal import Decimal
from django.db import models
from django.utils import timezone
from common.models import TenantModel


class FeeCategory(TenantModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["college", "code"],
                condition=models.Q(is_deleted=False),
                name="unique_fee_category_per_college",
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class FeeStructure(TenantModel):
    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    batch = models.ForeignKey(
        "academics.Batch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fee_structures",
    )
    semester_number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20, default="2026-2027")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    breakdown = models.JSONField(
        default=dict,
        help_text="Itemized breakdown, e.g. {'tuition': 45000, 'lab': 5000, 'library': 2000}",
    )

    class Meta:
        ordering = ["-academic_year", "course", "semester_number"]

    def __str__(self):
        return f"{self.title} - ₹{self.total_amount}"


class StudentInvoice(TenantModel):
    class InvoiceStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_number = models.CharField(max_length=50, db_index=True)
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    title = models.CharField(max_length=200)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING,
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["college", "invoice_number"],
                condition=models.Q(is_deleted=False),
                name="unique_invoice_number_per_college",
            )
        ]

    def recalculate_balance(self):
        self.final_amount = self.subtotal - self.discount_amount
        if self.final_amount < Decimal("0.00"):
            self.final_amount = Decimal("0.00")
        self.balance_due = self.final_amount - self.paid_amount
        if self.balance_due <= Decimal("0.00"):
            self.balance_due = Decimal("0.00")
            self.status = self.InvoiceStatus.PAID
        elif self.paid_amount > Decimal("0.00"):
            self.status = self.InvoiceStatus.PARTIALLY_PAID
        elif self.due_date < timezone.now().date():
            self.status = self.InvoiceStatus.OVERDUE
        else:
            self.status = self.InvoiceStatus.PENDING

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import uuid
            self.invoice_number = f"INV-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        self.recalculate_balance()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.student.roll_number} (₹{self.final_amount})"


class Payment(TenantModel):
    class PaymentMethod(models.TextChoices):
        UPI = "UPI", "UPI / QR Code"
        CARD = "CARD", "Debit / Credit Card"
        NET_BANKING = "NET_BANKING", "Net Banking"
        CASH = "CASH", "Cash"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer / NEFT"
        ONLINE = "ONLINE", "Online Gateway"

    class PaymentStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        PENDING = "PENDING", "Pending Verification"
        FAILED = "FAILED", "Failed"

    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.UPI,
    )
    transaction_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.SUCCESS,
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collected_payments",
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Payment ₹{self.amount} - {self.invoice.invoice_number} ({self.status})"


class PaymentReceipt(TenantModel):
    receipt_number = models.CharField(max_length=50, db_index=True)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="receipt",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="receipts",
    )
    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.CASCADE,
        related_name="receipts",
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["college", "receipt_number"],
                condition=models.Q(is_deleted=False),
                name="unique_receipt_number_per_college",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import uuid
            self.receipt_number = f"RCP-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.payment.amount}"
