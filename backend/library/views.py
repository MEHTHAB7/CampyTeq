from datetime import date
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsTenantMember
from library.models import Book, BookIssue
from library.serializers import (
    BookSerializer,
    BookIssueSerializer,
    BookIssueCreateSerializer,
    BookReturnActionSerializer,
)
from communication.models import Notification


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["category"]
    search_fields = ["title", "author", "isbn", "publisher", "shelf_location"]

    def get_queryset(self):
        return Book.objects.filter(college=self.request.user.college)

    def perform_create(self, serializer):
        serializer.save(college=self.request.user.college)


class BookIssueViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["status", "fine_paid", "book", "user"]
    search_fields = ["book__title", "book__isbn", "user__first_name", "user__last_name", "student__roll_number"]

    def get_serializer_class(self):
        if self.action == "create":
            return BookIssueCreateSerializer
        return BookIssueSerializer

    def get_queryset(self):
        user = self.request.user
        qs = BookIssue.objects.filter(college=user.college).select_related(
            "book", "user", "student", "issued_by"
        )
        if user.role in ["LIBRARY_STAFF", "SUPER_ADMIN", "PRINCIPAL"]:
            return qs
        return qs.filter(user=user)

    @action(detail=True, methods=["post"])
    def mark_return(self, request, pk=None):
        """Process book return, calculate overdue fine, and restock inventory."""
        issue = self.get_object()
        if issue.status == BookIssue.IssueStatus.RETURNED:
            return Response({"detail": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookReturnActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return_date = date.today()
        issue.return_date = return_date
        issue.status = BookIssue.IssueStatus.RETURNED

        fine = issue.calculate_overdue_fine(Decimal("5.00"))
        issue.fine_amount = fine
        issue.fine_paid = serializer.validated_data.get("fine_paid", False)
        if serializer.validated_data.get("remarks"):
            issue.remarks = f"{issue.remarks} | {serializer.validated_data['remarks']}".strip(" | ")

        issue.save()

        # Restock inventory
        book = issue.book
        book.available_copies += 1
        book.save()

        # Send notification to borrower
        Notification.objects.create(
            college=issue.college,
            recipient=issue.user,
            title=f"Library Return Confirmed: {book.title}",
            message=f"Book returned successfully.{f' Overdue fine assessed: ₹{fine}' if fine > 0 else ' No overdue fines.'}",
            notification_type="SYSTEM",
            action_url="/dashboard/library",
        )

        return Response(BookIssueSerializer(issue).data)

    @action(detail=False, methods=["get"])
    def overdue_list(self, request):
        today = date.today()
        qs = self.get_queryset().filter(
            status=BookIssue.IssueStatus.ISSUED,
            due_date__lt=today
        )
        serializer = BookIssueSerializer(qs, many=True)
        return Response(serializer.data)
