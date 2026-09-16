from decimal import Decimal
from datetime import date, timedelta
from rest_framework import serializers
from library.models import Book, BookIssue


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "author",
            "publisher",
            "edition",
            "publication_year",
            "category",
            "shelf_location",
            "total_copies",
            "available_copies",
            "is_available",
            "description",
            "cover_image_url",
            "created_at",
        ]


class BookIssueSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_isbn = serializers.CharField(source="book.isbn", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    student_roll = serializers.CharField(source="student.roll_number", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.get_full_name", read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            "id",
            "book",
            "book_title",
            "book_isbn",
            "book_author",
            "user",
            "user_name",
            "user_email",
            "student",
            "student_roll",
            "issued_by",
            "issued_by_name",
            "issue_date",
            "due_date",
            "return_date",
            "status",
            "fine_amount",
            "fine_paid",
            "remarks",
        ]
        read_only_fields = ["id", "issued_by", "return_date", "fine_amount", "fine_paid"]


class BookIssueCreateSerializer(serializers.ModelSerializer):
    issue_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)

    class Meta:
        model = BookIssue
        fields = ["id", "book", "user", "student", "issue_date", "due_date", "remarks", "status"]
        read_only_fields = ["id", "status"]

    def validate(self, attrs):
        book = attrs.get("book")
        if book.available_copies <= 0:
            raise serializers.ValidationError({"book": "All copies of this book are currently on loan."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        college = user.college
        book = validated_data["book"]

        issue_date = validated_data.get("issue_date") or date.today()
        due_date = validated_data.get("due_date") or (issue_date + timedelta(days=14))

        issue = BookIssue.objects.create(
            college=college,
            book=book,
            user=validated_data["user"],
            student=validated_data.get("student"),
            issued_by=user,
            issue_date=issue_date,
            due_date=due_date,
            remarks=validated_data.get("remarks", ""),
            status=BookIssue.IssueStatus.ISSUED,
        )

        # Decrement available copies
        book.available_copies -= 1
        book.save()

        return issue


class BookReturnActionSerializer(serializers.Serializer):
    fine_paid = serializers.BooleanField(default=False)
    remarks = serializers.CharField(required=False, allow_blank=True)


class LibraryRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)
    book_available = serializers.BooleanField(source="book.is_available", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        from library.models import LibraryRequest
        model = LibraryRequest
        fields = [
            "id",
            "user",
            "user_name",
            "user_role",
            "book",
            "book_title",
            "book_author",
            "book_available",
            "suggested_title",
            "request_type",
            "status",
            "notes",
            "reviewed_by",
            "reviewed_by_name",
            "reviewer_remarks",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "status", "reviewed_by", "reviewer_remarks", "reviewed_at", "created_at"]


class LibraryRequestReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["APPROVED", "REJECTED", "FULFILLED"])
    reviewer_remarks = serializers.CharField(required=False, allow_blank=True, default="")
