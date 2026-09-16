import pytest
from datetime import date, time
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from colleges.models import College
from departments.models import Department
from facilities.models import Facility, FacilityBooking
from library.models import Book, LibraryRequest


@pytest.mark.django_db
class TestFacilitiesAndLibraryWorkflow:
    def setup_method(self):
        self.client = APIClient()
        self.college = College.objects.create(name="Apex Tech", code="APEX-FAC", slug="apex-fac", status="ACTIVE")
        self.other_college = College.objects.create(name="Beta Univ", code="BETA-FAC", slug="beta-fac", status="ACTIVE")

        self.dept = Department.objects.create(college=self.college, name="Computer Science", code="CSE", status="ACTIVE")

        self.principal = User.objects.create_user(
            email="principal@apex.edu", password="Password123!", role="PRINCIPAL", college=self.college, first_name="Rajesh"
        )
        self.hod = User.objects.create_user(
            email="hod@apex.edu", password="Password123!", role="HOD", college=self.college, first_name="HOD CSE"
        )
        self.mentor = User.objects.create_user(
            email="mentor@apex.edu", password="Password123!", role="MENTOR", college=self.college, first_name="Mentor Joe"
        )
        self.faculty = User.objects.create_user(
            email="faculty@apex.edu", password="Password123!", role="FACULTY", college=self.college, first_name="Lab Fac"
        )
        self.student = User.objects.create_user(
            email="student@apex.edu", password="Password123!", role="STUDENT", college=self.college, first_name="Student Bob"
        )
        self.lib_staff = User.objects.create_user(
            email="lib@apex.edu", password="Password123!", role="LIBRARY_STAFF", college=self.college, first_name="Lib Staff"
        )

        self.hall = Facility.objects.create(
            college=self.college,
            name="Main Seminar Hall",
            facility_type="SEMINAR_HALL",
            capacity=300,
            location="Block A, 3rd Floor",
        )
        self.turf = Facility.objects.create(
            college=self.college,
            name="Campus Football Turf",
            facility_type="TURF",
            capacity=50,
            location="Sports Complex",
        )

        self.book = Book.objects.create(
            college=self.college,
            title="Clean Architecture",
            author="Robert C. Martin",
            isbn="9780134494166",
            category="CS",
            total_copies=5,
            available_copies=3,
        )

    def test_facility_booking_mentor_only(self):
        """Only Mentors can book Seminar Hall and Turf; Faculty and Students get 403."""
        # 1. Student blocked
        self.client.force_authenticate(user=self.student)
        res_stu = self.client.post("/api/v1/facilities/bookings/", {
            "facility": str(self.hall.id),
            "title": "Hackathon 2026",
            "purpose": "Annual college hackathon",
            "booking_date": "2026-10-15",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "department": str(self.dept.id),
        })
        assert res_stu.status_code == 403

        # 2. Faculty blocked
        self.client.force_authenticate(user=self.faculty)
        res_fac = self.client.post("/api/v1/facilities/bookings/", {
            "facility": str(self.hall.id),
            "title": "Lab Workshop",
            "purpose": "Hands-on lab",
            "booking_date": "2026-10-15",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "department": str(self.dept.id),
        })
        assert res_fac.status_code == 403

        # 3. Mentor creates booking
        self.client.force_authenticate(user=self.mentor)
        res_mentor = self.client.post("/api/v1/facilities/bookings/", {
            "facility": str(self.hall.id),
            "title": "AI Symposium 2026",
            "purpose": "Department technical symposium",
            "booking_date": "2026-10-15",
            "start_time": "10:00:00",
            "end_time": "16:00:00",
            "department": str(self.dept.id),
        })
        assert res_mentor.status_code == 201
        booking_id = res_mentor.data["id"]
        assert res_mentor.data["status"] == "PENDING"

        # 4. HOD approves booking
        self.client.force_authenticate(user=self.hod)
        appr_res = self.client.post(f"/api/v1/facilities/bookings/{booking_id}/review/", {
            "status": "APPROVED",
            "review_remarks": "Approved. Sound system setup included."
        })
        assert appr_res.status_code == 200
        assert appr_res.data["status"] == "APPROVED"

    def test_library_mentor_request_workflow(self):
        """Mentor requests book, library staff reviews and approves it."""
        # 1. Mentor requests a book
        self.client.force_authenticate(user=self.mentor)
        req_res = self.client.post("/api/v1/library/requests/", {
            "book": str(self.book.id),
            "request_type": "RESERVATION",
            "notes": "Reserve for mentoring session on design patterns",
        })
        assert req_res.status_code == 201
        req_id = req_res.data["id"]
        assert req_res.data["status"] == "PENDING"

        # 2. Library staff approves request
        self.client.force_authenticate(user=self.lib_staff)
        act_res = self.client.post(f"/api/v1/library/requests/{req_id}/review/", {
            "status": "APPROVED",
            "reviewer_remarks": "Kept on reserve shelf 2",
        })
        assert act_res.status_code == 200
        assert act_res.data["status"] == "APPROVED"
