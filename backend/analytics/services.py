from decimal import Decimal
from django.utils import timezone
from students.models import Student
from attendance.models import StudentAttendance
from assignments.models import Assignment, AssignmentSubmission
from exams.models import Result
from leave.models import LeaveRequest
from .models import StudentAIAnalysis


class AcademicRiskEngine:
    """
    Multi-factor academic risk evaluation engine.
    Computes explainable risk scores without ever taking automated punitive actions.
    """

    @classmethod
    def evaluate_student(cls, student: Student, analysis_type: str = 'ACADEMIC_EARLY_WARNING') -> StudentAIAnalysis:
        # 1. Attendance Metrics
        total_sessions = StudentAttendance.objects.filter(student=student).count()
        present_sessions = StudentAttendance.objects.filter(
            student=student,
            status__in=['PRESENT', 'LATE']
        ).count()
        attendance_rate = (
            round((present_sessions / total_sessions * 100), 2)
            if total_sessions > 0
            else 100.00
        )

        # 2. Assignment Metrics
        total_assignments = Assignment.objects.filter(
            batch=student.batch,
            status='ACTIVE'
        ).count()
        submitted_assignments = AssignmentSubmission.objects.filter(
            student=student,
            status__in=['SUBMITTED', 'LATE', 'GRADED']
        ).count()
        missing_assignments = max(0, total_assignments - submitted_assignments)

        # 3. Exam Result Metrics
        results = Result.objects.filter(student=student).select_related('exam_subject', 'exam_subject__exam')
        valid_results = [
            r for r in results 
            if r.exam_subject and r.exam_subject.exam and r.exam_subject.exam.is_published and r.exam_subject.maximum_marks > 0
        ]
        if valid_results:
            total_pct = sum(
                (float(r.marks_obtained) / float(r.exam_subject.maximum_marks)) * 100.0
                for r in valid_results
            )
            avg_marks = round(total_pct / len(valid_results), 2)
        else:
            avg_marks = 75.00

        # 4. Leave Pattern Metrics
        approved_leaves = LeaveRequest.objects.filter(user=student.user, status='APPROVED')
        total_leave_days = sum(l.days_count for l in approved_leaves)

        # 5. Multi-Factor Risk Calculation
        risk_score = 0.0
        drivers = []
        interventions = []

        # Attendance evaluation (weight up to 50 pts)
        if attendance_rate < 50.0:
            risk_score += 50.0
            drivers.append(f"Severe attendance deficit: current attendance is {attendance_rate}% (critical statutory defaulter).")
        elif attendance_rate < 65.0:
            risk_score += 35.0
            drivers.append(f"Chronic attendance shortage: current attendance is {attendance_rate}% (defaulter under mandatory 75% rule).")
        elif attendance_rate < 75.0:
            risk_score += 25.0
            drivers.append(f"Attendance {attendance_rate}% is below the mandatory 75% minimum semester examination threshold.")
        elif attendance_rate < 80.0:
            risk_score += 10.0
            drivers.append(f"Marginal attendance {attendance_rate}% approaching defaulter threshold.")
        else:
            drivers.append(f"Satisfactory attendance standing ({attendance_rate}%).")

        # Assignment completion evaluation (weight up to 25 pts)
        if missing_assignments >= 2:
            risk_score += 25.0
            drivers.append(f"{missing_assignments} mandatory coursework assignments are missing or unsubmitted.")
        elif missing_assignments == 1:
            risk_score += 12.0
            drivers.append("1 course assignment is overdue and unsubmitted.")
        else:
            drivers.append("Course assignments are up to date.")

        # Examination trajectory evaluation (weight up to 25 pts)
        if avg_marks < 40.0:
            risk_score += 25.0
            drivers.append(f"Critical examination underperformance: current subject average is {avg_marks}%.")
        elif avg_marks < 55.0:
            risk_score += 15.0
            drivers.append(f"Below-average examination performance: subject average is {avg_marks}%.")
        elif avg_marks < 65.0:
            risk_score += 8.0
            drivers.append(f"Moderate examination results: subject average is {avg_marks}%.")
        else:
            drivers.append(f"Strong academic examination trajectory ({avg_marks}% average).")

        # Leave frequency evaluation (weight up to 10 pts)
        if total_leave_days > 5:
            risk_score += 10.0
            drivers.append(f"Frequent absences: {total_leave_days} approved leave days recorded this term.")

        # Clamp composite score
        composite_score = round(min(100.00, max(0.00, risk_score)), 2)

        # Categorize risk level
        if composite_score >= 90.0:
            risk_level = 'CRITICAL'
        elif composite_score >= 70.0:
            risk_level = 'HIGH'
        elif composite_score >= 40.0:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        # Recommended interventions
        if risk_level in ['CRITICAL', 'HIGH']:
            interventions.append("Schedule mandatory 1-on-1 mentor academic review & counseling session.")
            interventions.append("Enroll in departmental remedial tutorial classes in deficient subjects.")
            interventions.append("Issue formal attendance advisory letter to parent/guardian regarding exam eligibility.")
        elif risk_level == 'MEDIUM':
            interventions.append("Conduct mentor check-in regarding pending coursework and lab assignments.")
            interventions.append("Recommend peer study group participation for upcoming evaluations.")
        else:
            interventions.append("Maintain existing academic consistency and attendance discipline.")
            interventions.append("Eligible for advanced research electives and honors project tracks.")

        # Snapshot of metric inputs
        snapshot = {
            "total_attendance_sessions": total_sessions,
            "present_sessions": present_sessions,
            "attendance_rate": attendance_rate,
            "missing_assignments": missing_assignments,
            "average_marks": avg_marks,
            "total_leave_days": total_leave_days,
            "evaluation_timestamp": timezone.now().isoformat(),
        }

        # Demote previous analysis records for this student
        StudentAIAnalysis.objects.filter(student=student, is_latest=True).update(is_latest=False)

        # Create new latest record
        analysis = StudentAIAnalysis.objects.create(
            college=student.college,
            student=student,
            risk_level=risk_level,
            score=Decimal(str(composite_score)),
            analysis_type=analysis_type,
            attendance_rate=Decimal(str(attendance_rate)),
            missing_assignments_count=missing_assignments,
            average_marks_percentage=Decimal(str(avg_marks)),
            leave_days_count=total_leave_days,
            key_risk_drivers=drivers,
            suggested_interventions=interventions,
            input_snapshot=snapshot,
            is_latest=True
        )

        return analysis
