from django.contrib import admin
from facilities.models import Facility, FacilityBooking

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ["name", "facility_type", "capacity", "location", "is_active", "college"]
    list_filter = ["facility_type", "is_active", "college"]
    search_fields = ["name", "location"]

@admin.register(FacilityBooking)
class FacilityBookingAdmin(admin.ModelAdmin):
    list_display = ["facility", "requested_by", "booking_date", "start_time", "end_time", "status", "college"]
    list_filter = ["status", "booking_date", "facility__facility_type", "college"]
    search_fields = ["purpose", "requested_by__email", "facility__name"]
