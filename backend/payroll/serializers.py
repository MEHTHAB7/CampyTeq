from rest_framework import serializers
from payroll.models import SalaryStructure, Payslip


class SalaryStructureSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.user.get_full_name", read_only=True)
    faculty_number = serializers.CharField(source="faculty.faculty_number", read_only=True)
    department_name = serializers.CharField(source="faculty.department.name", read_only=True)
    gross_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_salary = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = SalaryStructure
        fields = [
            "id",
            "faculty",
            "faculty_name",
            "faculty_number",
            "department_name",
            "basic_salary",
            "hra",
            "da",
            "special_allowance",
            "pf_deduction",
            "tax_deduction",
            "other_deductions",
            "gross_salary",
            "total_deductions",
            "net_salary",
        ]


class PayslipSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.user.get_full_name", read_only=True)
    faculty_number = serializers.CharField(source="faculty.faculty_number", read_only=True)
    department_name = serializers.CharField(source="faculty.department.name", read_only=True)
    designation = serializers.CharField(source="faculty.designation", read_only=True)

    class Meta:
        model = Payslip
        fields = [
            "id",
            "payslip_number",
            "faculty",
            "faculty_name",
            "faculty_number",
            "department_name",
            "designation",
            "month",
            "year",
            "working_days",
            "present_days",
            "leave_days",
            "basic_salary",
            "allowances",
            "gross_salary",
            "deductions",
            "tax_deducted",
            "net_salary",
            "status",
            "payment_date",
            "payment_method",
            "transaction_ref",
            "remarks",
            "created_at",
        ]
        read_only_fields = ["payslip_number", "gross_salary", "net_salary", "created_at"]


class GeneratePayrollSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2020, max_value=2050)
