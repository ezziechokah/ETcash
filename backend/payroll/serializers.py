from rest_framework import serializers

from .models import Employee, PayrollRun, Payslip


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_number', 'full_name', 'email', 'phone',
            'kra_pin', 'nssf_number', 'nhif_number', 'basic_salary',
            'bank_account', 'is_active', 'created_at',
        ]


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(read_only=True)

    class Meta:
        model = Payslip
        fields = ['id', 'employee', 'employee_name', 'gross', 'nssf', 'nhif', 'paye', 'net']


class PayrollRunSerializer(serializers.ModelSerializer):
    payslips = PayslipSerializer(many=True, read_only=True)
    period_label = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            'id', 'period_month', 'period_year', 'period_label', 'status',
            'total_gross', 'total_net', 'payslips', 'created_at',
        ]

    def get_period_label(self, obj):
        months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f'{months[obj.period_month]} {obj.period_year}'


class PayrollRunListSerializer(serializers.ModelSerializer):
    period_label = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            'id', 'period_month', 'period_year', 'period_label',
            'status', 'total_gross', 'total_net', 'employee_count', 'created_at',
        ]

    def get_employee_count(self, obj):
        return obj.payslips.count()

    def get_period_label(self, obj):
        months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f'{months[obj.period_month]} {obj.period_year}'
