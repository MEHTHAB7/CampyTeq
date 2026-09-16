from rest_framework import serializers
from facilities.models import Facility, FacilityBooking


class FacilitySerializer(serializers.ModelSerializer):
    facility_type_display = serializers.CharField(source="get_facility_type_display", read_only=True)

    class Meta:
        model = Facility
        fields = [
            "id",
            "name",
            "facility_type",
            "facility_type_display",
            "capacity",
            "location",
            "description",
            "amenities",
            "is_active",
            "created_at",
        ]


class FacilityBookingSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    facility_type = serializers.CharField(source="facility.facility_type", read_only=True)
    facility_location = serializers.CharField(source="facility.location", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    requested_by_role = serializers.CharField(source="requested_by.role", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True, default="")
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True, default="")

    class Meta:
        model = FacilityBooking
        fields = [
            "id",
            "facility",
            "facility_name",
            "facility_type",
            "facility_location",
            "requested_by",
            "requested_by_name",
            "requested_by_role",
            "department",
            "department_name",
            "booking_date",
            "start_time",
            "end_time",
            "purpose",
            "expected_attendees",
            "notes",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_remarks",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "requested_by",
            "department",
            "status",
            "reviewed_by",
            "review_remarks",
            "reviewed_at",
            "created_at",
        ]


class FacilityBookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityBooking
        fields = [
            "id",
            "facility",
            "booking_date",
            "start_time",
            "end_time",
            "purpose",
            "expected_attendees",
            "notes",
            "status",
        ]
        read_only_fields = ["id", "status"]

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError({"end_time": "End time must be strictly after start time."})
        
        # Check conflict with existing approved bookings
        facility = attrs.get("facility")
        b_date = attrs.get("booking_date")
        if facility and b_date and start and end:
            overlapping = FacilityBooking.objects.filter(
                facility=facility,
                booking_date=b_date,
                status="APPROVED",
                start_time__lt=end,
                end_time__gt=start,
            ).exists()
            if overlapping:
                raise serializers.ValidationError({
                    "non_field_errors": [
                        f"{facility.name} already has an approved reservation during this time window."
                    ]
                })

        return attrs


class FacilityBookingReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["APPROVED", "REJECTED"])
    review_remarks = serializers.CharField(required=False, allow_blank=True, default="")
