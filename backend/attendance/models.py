from datetime import datetime, timedelta
from django.db import models
from common.models import TenantModel


class AttendanceSession(TenantModel):
    class SessionType(models.TextChoices):
        REGULAR = "REGULAR", "Regular Lecture"
        LAB = "LAB", "Lab Practical"
        EXTRA = "EXTRA", "Extra Class"
        TUTORIAL = "TUTORIAL", "Tutorial"

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="conducted_sessions",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.REGULAR,
    )
    topic_covered = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.subject.code} - {self.date} ({self.start_time.strftime('%H:%M')})"

    @property
    def total_students(self):
        return self.student_attendances.count()

    @property
    def present_count(self):
        return self.student_attendances.filter(status__in=["PRESENT", "LATE"]).count()

    @property
    def absent_count(self):
        return self.student_attendances.filter(status="ABSENT").count()


class StudentAttendance(TenantModel):
    class AttendanceStatus(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        EXCUSED = "EXCUSED", "Excused"

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="student_attendances",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_student_attendances",
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("session", "student")
        ordering = ["student__roll_number"]

    def __str__(self):
        return f"{self.student.roll_number} - {self.session.subject.code} ({self.status})"


class FacultyAttendance(TenantModel):
    class FacultyStatus(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        HALF_DAY = "HALF_DAY", "Half Day"
        ABSENT = "ABSENT", "Absent"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    class PunchSource(models.TextChoices):
        WEB_PORTAL = "WEB_PORTAL", "Web Portal"
        BIOMETRIC = "BIOMETRIC", "Biometric Fingerprint"
        RFID = "RFID", "RFID Card Tap"
        MANUAL = "MANUAL", "Manual Admin Entry"

    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    working_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=FacultyStatus.choices,
        default=FacultyStatus.PRESENT,
    )
    punch_source = models.CharField(
        max_length=20,
        choices=PunchSource.choices,
        default=PunchSource.WEB_PORTAL,
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("faculty", "date")
        ordering = ["-date"]

    def calculate_working_minutes(self):
        if self.check_in and self.check_out:
            t1 = datetime.combine(self.date, self.check_in)
            t2 = datetime.combine(self.date, self.check_out)
            if t2 > t1:
                diff = t2 - t1
                self.working_minutes = int(diff.total_seconds() // 60)
            else:
                self.working_minutes = 0
        return self.working_minutes

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            self.calculate_working_minutes()
            # If worked less than 4 hours (240 min), mark half day
            if self.working_minutes > 0 and self.working_minutes < 240:
                self.status = self.FacultyStatus.HALF_DAY
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.faculty.faculty_number} - {self.date} ({self.status})"
