from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsTenantMember
from printshop.models import PrintPricing, PrintOrder
from printshop.serializers import (
    PrintPricingSerializer,
    PrintOrderSerializer,
    PrintOrderCreateSerializer,
    PrintStatusUpdateSerializer,
)
from communication.models import Notification


class PrintPricingViewSet(viewsets.ModelViewSet):
    serializer_class = PrintPricingSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return PrintPricing.objects.filter(college=self.request.user.college)

    def list(self, request, *args, **kwargs):
        pricing, _ = PrintPricing.objects.get_or_create(college=request.user.college)
        serializer = self.get_serializer(pricing)
        return Response(serializer.data)


class PrintOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["status", "payment_status", "print_color"]
    search_fields = ["order_number", "document_name", "user__first_name", "user__last_name"]

    def get_serializer_class(self):
        if self.action == "create":
            return PrintOrderCreateSerializer
        return PrintOrderSerializer

    def get_queryset(self):
        user = self.request.user
        qs = PrintOrder.objects.filter(college=user.college).select_related(
            "user", "handled_by"
        )
        if user.role in ["PRINT_STAFF", "SUPER_ADMIN", "PRINCIPAL"]:
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=["post"])
    def calculate_price(self, request):
        """Estimate price for given options before ordering."""
        pricing, _ = PrintPricing.objects.get_or_create(college=request.user.college)

        page_count = int(request.data.get("page_count", 1))
        copies = int(request.data.get("copies", 1))
        print_color = request.data.get("print_color", "BW")
        print_side = request.data.get("print_side", "SINGLE")
        paper_size = request.data.get("paper_size", "A4")
        binding_type = request.data.get("binding_type", "NONE")
        lamination = bool(request.data.get("lamination", False))

        dummy_order = PrintOrder(
            college=request.user.college,
            user=request.user,
            page_count=page_count,
            copies=copies,
            print_color=print_color,
            print_side=print_side,
            paper_size=paper_size,
            binding_type=binding_type,
            lamination=lamination,
        )
        cost = dummy_order.calculate_cost(pricing)
        return Response({"estimated_amount": str(cost)})

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = PrintStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        order.status = new_status
        order.handled_by = request.user

        if new_status == PrintOrder.OrderStatus.COMPLETED:
            order.completed_at = timezone.now()
            order.payment_status = PrintOrder.PaymentStatus.PAID
        elif new_status == PrintOrder.OrderStatus.READY_FOR_PICKUP:
            # Notify ordering student/faculty
            Notification.objects.create(
                college=order.college,
                recipient=order.user,
                title=f"Print Order Ready: {order.document_name}",
                message=f"Order {order.order_number} is ready for collection at the Campus Print Station.",
                notification_type="SYSTEM",
                action_url="/dashboard/printshop",
            )

        order.save()
        return Response(PrintOrderSerializer(order).data)
