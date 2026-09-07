from rest_framework import serializers
from decimal import Decimal
from fees.models import FeeCategory, FeeStructure, StudentInvoice, Payment, PaymentReceipt


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ["id", "name", "code", "description"]


class FeeStructureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            "id",
            "course",
            "course_name",
            "course_code",
            "batch",
            "semester_number",
            "title",
            "academic_year",
            "total_amount",
            "breakdown",
        ]


class PaymentReceiptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_roll = serializers.CharField(source="student.roll_number", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    amount = serializers.DecimalField(source="payment.amount", max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(source="payment.payment_method", read_only=True)
    transaction_reference = serializers.CharField(source="payment.transaction_reference", read_only=True)
    college_name = serializers.CharField(source="college.name", read_only=True)

    class Meta:
        model = PaymentReceipt
        fields = [
            "id",
            "receipt_number",
            "student",
            "student_name",
            "student_roll",
            "invoice",
            "invoice_number",
            "amount",
            "payment_method",
            "transaction_reference",
            "college_name",
            "issued_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_roll = serializers.CharField(source="student.roll_number", read_only=True)
    received_by_name = serializers.CharField(source="received_by.get_full_name", read_only=True)
    receipt_number = serializers.CharField(source="receipt.receipt_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "student",
            "student_name",
            "student_roll",
            "amount",
            "payment_method",
            "transaction_reference",
            "status",
            "paid_at",
            "received_by",
            "received_by_name",
            "receipt_number",
            "remarks",
        ]
        read_only_fields = ["paid_at", "received_by"]


class StudentInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_roll = serializers.CharField(source="student.roll_number", read_only=True)
    department_name = serializers.CharField(source="student.department.name", read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentInvoice
        fields = [
            "id",
            "invoice_number",
            "student",
            "student_name",
            "student_roll",
            "department_name",
            "fee_structure",
            "title",
            "subtotal",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "balance_due",
            "due_date",
            "status",
            "remarks",
            "payments",
            "created_at",
        ]
        read_only_fields = ["invoice_number", "final_amount", "paid_amount", "balance_due", "created_at"]


class InvoicePaymentActionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices,
        default=Payment.PaymentMethod.UPI,
    )
    transaction_reference = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
