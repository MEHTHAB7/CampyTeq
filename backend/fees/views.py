import uuid
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Count, Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsTenantMember
from fees.models import FeeCategory, FeeStructure, StudentInvoice, Payment, PaymentReceipt
from fees.serializers import (
    FeeCategorySerializer,
    FeeStructureSerializer,
    StudentInvoiceSerializer,
    InvoicePaymentActionSerializer,
    PaymentSerializer,
    PaymentReceiptSerializer,
)


class FeeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return FeeCategory.objects.filter(college=self.request.user.college)

    def perform_create(self, serializer):
        serializer.save(college=self.request.user.college)


class FeeStructureViewSet(viewsets.ModelViewSet):
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["course", "batch", "semester_number", "academic_year"]

    def get_queryset(self):
        return FeeStructure.objects.filter(
            college=self.request.user.college
        ).select_related("course", "batch")

    def perform_create(self, serializer):
        serializer.save(college=self.request.user.college)


class StudentInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["status", "student", "due_date"]
    search_fields = ["invoice_number", "student__user__first_name", "student__user__last_name", "student__roll_number"]

    def get_queryset(self):
        user = self.request.user
        qs = StudentInvoice.objects.filter(
            college=user.college
        ).select_related("student", "student__user", "student__department", "fee_structure")

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                return qs.filter(student=user.student_profile)
            return StudentInvoice.objects.none()
        elif user.role == "PARENT":
            from students.models import StudentGuardian
            ward_ids = StudentGuardian.objects.filter(
                guardian__user=user
            ).values_list("student_id", flat=True)
            return qs.filter(student_id__in=ward_ids)
        return qs

    def perform_create(self, serializer):
        serializer.save(college=self.request.user.college)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        """Processes payment towards an invoice, updates balance, and generates digital receipt."""
        invoice = self.get_object()
        serializer = InvoicePaymentActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pay_amount = serializer.validated_data["amount"]
        if pay_amount <= Decimal("0.00"):
            return Response(
                {"error": "Payment amount must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if pay_amount > invoice.balance_due:
            return Response(
                {"error": f"Payment amount (₹{pay_amount}) exceeds remaining balance (₹{invoice.balance_due})"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_method = serializer.validated_data.get("payment_method", "UPI")
        tx_ref = serializer.validated_data.get("transaction_reference")
        if not tx_ref:
            tx_ref = f"TXN-{uuid.uuid4().hex[:8].upper()}"

        with transaction.atomic():
            # 1. Create Payment record
            payment = Payment.objects.create(
                college=invoice.college,
                invoice=invoice,
                student=invoice.student,
                amount=pay_amount,
                payment_method=payment_method,
                transaction_reference=tx_ref,
                status="SUCCESS",
                received_by=request.user,
                remarks=serializer.validated_data.get("remarks", ""),
            )

            # 2. Create Receipt
            receipt = PaymentReceipt.objects.create(
                college=invoice.college,
                payment=payment,
                student=invoice.student,
                invoice=invoice,
            )

            # 3. Update invoice paid amount
            invoice.paid_amount += pay_amount
            invoice.recalculate_balance()
            invoice.save()

        return Response({
            "message": f"Successfully processed payment of ₹{pay_amount}",
            "invoice": StudentInvoiceSerializer(invoice).data,
            "payment": PaymentSerializer(payment).data,
            "receipt": PaymentReceiptSerializer(receipt).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def pending_summary(self, request):
        """Returns aggregate financial KPI summary for accountant/principal."""
        user = request.user
        invoices = StudentInvoice.objects.filter(college=user.college)

        totals = invoices.aggregate(
            total_billed=Sum("final_amount"),
            total_collected=Sum("paid_amount"),
            total_outstanding=Sum("balance_due"),
            total_count=Count("id"),
        )

        pending_count = invoices.filter(status__in=["PENDING", "PARTIALLY_PAID"]).count()
        overdue_count = invoices.filter(status="OVERDUE").count()
        paid_count = invoices.filter(status="PAID").count()

        return Response({
            "total_billed": totals["total_billed"] or Decimal("0.00"),
            "total_collected": totals["total_collected"] or Decimal("0.00"),
            "total_outstanding": totals["total_outstanding"] or Decimal("0.00"),
            "total_invoices": totals["total_count"] or 0,
            "pending_invoices": pending_count,
            "overdue_invoices": overdue_count,
            "paid_invoices": paid_count,
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["payment_method", "status", "student", "invoice"]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.filter(
            college=user.college
        ).select_related("invoice", "student", "student__user", "received_by")

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                return qs.filter(student=user.student_profile)
            return Payment.objects.none()
        return qs


class PaymentReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentReceiptSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    search_fields = ["receipt_number", "invoice__invoice_number", "student__roll_number"]

    def get_queryset(self):
        user = self.request.user
        qs = PaymentReceipt.objects.filter(
            college=user.college
        ).select_related("payment", "student", "student__user", "invoice", "college")

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                return qs.filter(student=user.student_profile)
            return PaymentReceipt.objects.none()
        return qs
