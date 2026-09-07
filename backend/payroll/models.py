from decimal import Decimal
from django.db import models
from django.utils import timezone
from common.models import TenantModel


class SalaryStructure(TenantModel):
    faculty = models.OneToOneField(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="salary_structure",
    )
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="House Rent Allowance")
    da = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="Dearness Allowance")
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="Provident Fund")
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="TDS / Income Tax")
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    @property
    def gross_salary(self):
        return self.basic_salary + self.hra + self.da + self.special_allowance

    @property
    def total_deductions(self):
        return self.pf_deduction + self.tax_deduction + self.other_deductions

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions

    def __str__(self):
        return f"{self.faculty.faculty_number} - Net: ₹{self.net_salary}"


class Payslip(TenantModel):
    class PayslipStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PROCESSED = "PROCESSED", "Processed"
        PAID = "PAID", "Disbursed / Paid"

    payslip_number = models.CharField(max_length=50, db_index=True)
    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="payslips",
    )
    month = models.PositiveSmallIntegerField(help_text="1 to 12")
    year = models.PositiveSmallIntegerField()
    working_days = models.PositiveSmallIntegerField(default=30)
    present_days = models.PositiveSmallIntegerField(default=30)
    leave_days = models.PositiveSmallIntegerField(default=0)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PayslipStatus.choices,
        default=PayslipStatus.PROCESSED,
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, default="DIRECT_DEPOSIT")
    transaction_ref = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["college", "faculty", "month", "year"],
                condition=models.Q(is_deleted=False),
                name="unique_payslip_per_faculty_month",
            ),
            models.UniqueConstraint(
                fields=["college", "payslip_number"],
                condition=models.Q(is_deleted=False),
                name="unique_payslip_number_per_college",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.payslip_number:
            import uuid
            self.payslip_number = f"PAY-{self.year}{self.month:02d}-{uuid.uuid4().hex[:6].upper()}"
        self.gross_salary = self.basic_salary + self.allowances
        self.net_salary = self.gross_salary - self.deductions - self.tax_deducted
        if self.net_salary < Decimal("0.00"):
            self.net_salary = Decimal("0.00")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payslip_number} - {self.faculty.faculty_number} ({self.month}/{self.year}) ₹{self.net_salary}"
