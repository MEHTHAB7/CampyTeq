from datetime import datetime, date
from django.db.models import Count, Q, F
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsTenantMember
from attendance.models import AttendanceSession, StudentAttendance, FacultyAttendance
from attendance.serializers import (
    AttendanceSessionSerializer,
    AttendanceSessionDetailSerializer,
    StudentAttendanceSerializer,
    BulkMarkAttendanceSerializer,
    FacultyAttendanceSerializer,
    FacultyPunchSerializer,
)
from students.models import Student
from academics.models import Subject


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["date", "subject", "semester", "faculty", "session_type"]
    search_fields = ["subject__name", "subject__code", "topic_covered"]

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceSession.objects.filter(
            college=user.college
        ).select_related("subject", "semester", "faculty", "faculty__user")

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                qs = qs.filter(semester=user.student_profile.current_semester)
            else:
                return AttendanceSession.objects.none()
        elif user.role == "FACULTY":
            if hasattr(user, "faculty_profile"):
                qs = qs.filter(faculty=user.faculty_profile)
        return qs

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return AttendanceSessionDetailSerializer
        return AttendanceSessionSerializer

    def perform_create(self, serializer):
        user = self.request.user
        faculty = serializer.validated_data.get("faculty")
        if not faculty and hasattr(user, "faculty_profile"):
            faculty = user.faculty_profile
        serializer.save(college=user.college, faculty=faculty)

    @action(detail=True, methods=["get"])
    def roster(self, request, pk=None):
        """Returns the enrolled student roster for this session's semester, along with current mark status if any."""
        session = self.get_object()
        students = Student.objects.filter(
            college=session.college,
            current_semester=session.semester,
            status="ACTIVE",
        ).select_related("user")

        # Map existing attendance
        existing_attendances = {
            att.student_id: att for att in session.student_attendances.all()
        }

        roster_data = []
        for s in students:
            att = existing_attendances.get(s.id)
            roster_data.append({
                "student_id": str(s.id),
                "student_name": s.user.get_full_name(),
                "roll_number": s.roll_number,
                "status": att.status if att else None,
                "remarks": att.remarks if att else "",
            })
        return Response(roster_data)

    @action(detail=True, methods=["post"])
    def mark_bulk(self, request, pk=None):
        """Allows faculty to mark attendance for all students in one request."""
        session = self.get_object()
        serializer = BulkMarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attendances_data = serializer.validated_data["attendances"]
        records_to_create = []
        records_to_update = []

        existing_records = {
            att.student_id: att for att in session.student_attendances.all()
        }

        for item in attendances_data:
            student_id = item["student_id"]
            new_status = item["status"]
            remarks = item.get("remarks", "")

            if student_id in existing_records:
                record = existing_records[student_id]
                record.status = new_status
                record.remarks = remarks
                record.marked_by = request.user
                records_to_update.append(record)
            else:
                records_to_create.append(
                    StudentAttendance(
                        college=session.college,
                        session=session,
                        student_id=student_id,
                        status=new_status,
                        remarks=remarks,
                        marked_by=request.user,
                    )
                )

        if records_to_create:
            StudentAttendance.objects.bulk_create(records_to_create)
        if records_to_update:
            StudentAttendance.objects.bulk_update(
                records_to_update, ["status", "remarks", "marked_by"]
            )

        return Response({
            "message": f"Successfully updated attendance for {len(attendances_data)} students.",
            "created": len(records_to_create),
            "updated": len(records_to_update),
        })


class StudentAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["session", "student", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = StudentAttendance.objects.filter(
            college=user.college
        ).select_related(
            "session", "session__subject", "student", "student__user", "marked_by"
        )

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                return qs.filter(student=user.student_profile)
            return StudentAttendance.objects.none()
        elif user.role == "PARENT":
            from students.models import StudentGuardian
            ward_ids = StudentGuardian.objects.filter(
                guardian__user=user
            ).values_list("student_id", flat=True)
            return qs.filter(student_id__in=ward_ids)
        elif user.role == "MENTOR":
            if hasattr(user, "faculty_profile"):
                from students.models import MentorAssignment
                assigned_student_ids = MentorAssignment.objects.filter(
                    mentor=user.faculty_profile, is_active=True
                ).values_list("student_id", flat=True)
                return qs.filter(student_id__in=assigned_student_ids)
            return StudentAttendance.objects.none()
        return qs

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Returns subject-wise and overall attendance percentage for a student."""
        user = request.user
        student_id = request.query_params.get("student_id")

        if user.role == "STUDENT":
            if hasattr(user, "student_profile"):
                student = user.student_profile
            else:
                return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)
        elif student_id:
            try:
                student = Student.objects.get(id=student_id, college=user.college)
            except Student.DoesNotExist:
                return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "student_id is required for staff queries"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate attendance per subject
        subjects = Subject.objects.filter(
            course=student.course,
            semester_number=student.current_semester.semester_number,
            college=student.college,
        )

        subject_summaries = []
        total_conducted_all = 0
        total_attended_all = 0

        for subj in subjects:
            sessions = AttendanceSession.objects.filter(
                subject=subj, semester=student.current_semester, college=student.college
            )
            conducted_count = sessions.count()
            attended_count = StudentAttendance.objects.filter(
                session__in=sessions,
                student=student,
                status__in=["PRESENT", "LATE"],
            ).count()

            percentage = round((attended_count / conducted_count * 100), 2) if conducted_count > 0 else 100.0
            is_low = percentage < 75.0

            total_conducted_all += conducted_count
            total_attended_all += attended_count

            subject_summaries.append({
                "subject_id": str(subj.id),
                "subject_code": subj.code,
                "subject_name": subj.name,
                "credits": subj.credits,
                "conducted_sessions": conducted_count,
                "attended_sessions": attended_count,
                "percentage": percentage,
                "is_low_attendance": is_low,
            })

        overall_percentage = (
            round((total_attended_all / total_conducted_all * 100), 2)
            if total_conducted_all > 0
            else 100.0
        )

        return Response({
            "student_id": str(student.id),
            "student_name": student.user.get_full_name(),
            "roll_number": student.roll_number,
            "overall_conducted": total_conducted_all,
            "overall_attended": total_attended_all,
            "overall_percentage": overall_percentage,
            "is_defaulter": overall_percentage < 75.0,
            "subjects": subject_summaries,
        })

    @action(detail=False, methods=["get"])
    def defaulters(self, request):
        """Returns list of students with overall attendance below 75%."""
        user = request.user
        students_qs = Student.objects.filter(
            college=user.college, status="ACTIVE"
        ).select_related("user", "department", "current_semester", "mentor", "mentor__user")

        if user.role == "MENTOR" and hasattr(user, "faculty_profile"):
            from students.models import MentorAssignment
            assigned_student_ids = MentorAssignment.objects.filter(
                mentor=user.faculty_profile, is_active=True
            ).values_list("student_id", flat=True)
            students_qs = students_qs.filter(id__in=assigned_student_ids)

        defaulters_list = []
        for s in students_qs:
            sessions = AttendanceSession.objects.filter(
                semester=s.current_semester, college=s.college
            )
            conducted = sessions.count()
            if conducted == 0:
                continue

            attended = StudentAttendance.objects.filter(
                session__in=sessions,
                student=s,
                status__in=["PRESENT", "LATE"],
            ).count()

            pct = round((attended / conducted * 100), 2)
            if pct < 75.0:
                defaulters_list.append({
                    "student_id": str(s.id),
                    "student_name": s.user.get_full_name(),
                    "roll_number": s.roll_number,
                    "department_name": s.department.name if s.department else "N/A",
                    "semester_name": s.current_semester.name if s.current_semester else "N/A",
                    "attendance_percentage": pct,
                    "conducted_sessions": conducted,
                    "attended_sessions": attended,
                    "missed_sessions": conducted - attended,
                    "mentor_name": s.mentor.user.get_full_name() if s.mentor else "Not Assigned",
                    "mentor_email": s.mentor.user.email if s.mentor else "",
                })

        return Response(defaulters_list)


class FacultyAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = FacultyAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filterset_fields = ["date", "faculty", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = FacultyAttendance.objects.filter(
            college=user.college
        ).select_related("faculty", "faculty__user", "faculty__department")

        if user.role == "FACULTY":
            if hasattr(user, "faculty_profile"):
                return qs.filter(faculty=user.faculty_profile)
            return FacultyAttendance.objects.none()
        return qs

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Returns the authenticated faculty member's punch status for today."""
        user = request.user
        if not hasattr(user, "faculty_profile"):
            return Response({"error": "Faculty profile required"}, status=status.HTTP_400_BAD_REQUEST)

        today_date = timezone.localdate() if hasattr(timezone, "localdate") else date.today()
        record = FacultyAttendance.objects.filter(
            faculty=user.faculty_profile, date=today_date
        ).first()

        if record:
            return Response(FacultyAttendanceSerializer(record).data)
        return Response({
            "is_punched_in": False,
            "is_punched_out": False,
            "date": str(today_date),
            "record": None,
        })

    @action(detail=False, methods=["post"])
    def check_in(self, request):
        """Records check-in punch for authenticated faculty."""
        user = request.user
        if not hasattr(user, "faculty_profile"):
            return Response({"error": "Faculty profile required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FacultyPunchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = timezone.localtime() if hasattr(timezone, "localtime") else datetime.now()
        today_date = now.date()
        current_time = now.time()

        record, created = FacultyAttendance.objects.get_or_create(
            college=user.college,
            faculty=user.faculty_profile,
            date=today_date,
            defaults={
                "check_in": current_time,
                "punch_source": serializer.validated_data.get("punch_source", "WEB_PORTAL"),
                "remarks": serializer.validated_data.get("remarks", ""),
                "status": "PRESENT",
            },
        )

        if not created and not record.check_in:
            record.check_in = current_time
            record.punch_source = serializer.validated_data.get("punch_source", "WEB_PORTAL")
            record.save()

        return Response(FacultyAttendanceSerializer(record).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def check_out(self, request):
        """Records check-out punch and computes working duration."""
        user = request.user
        if not hasattr(user, "faculty_profile"):
            return Response({"error": "Faculty profile required"}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.localtime() if hasattr(timezone, "localtime") else datetime.now()
        today_date = now.date()
        current_time = now.time()

        record = FacultyAttendance.objects.filter(
            faculty=user.faculty_profile, date=today_date
        ).first()

        if not record:
            return Response(
                {"error": "Cannot check out without a valid check-in today"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record.check_out = current_time
        record.save()  # Triggers calculate_working_minutes in model save()

        return Response(FacultyAttendanceSerializer(record).data, status=status.HTTP_200_OK)
