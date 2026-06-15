from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import CompanyScopedMixin

from .kenya import compute_payslip
from .models import Employee, PayrollRun, Payslip
from .serializers import EmployeeSerializer, PayrollRunListSerializer, PayrollRunSerializer


class EmployeeViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class PayrollRunViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = PayrollRun.objects.prefetch_related('payslips', 'payslips__employee')

    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollRunListSerializer
        return PayrollRunSerializer

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        run = self.get_object()
        if run.status != 'draft':
            return Response({'detail': 'Run already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        run.payslips.all().delete()
        employees = Employee.objects.filter(company=run.company, is_active=True)
        total_gross = Decimal('0')
        total_net = Decimal('0')

        for emp in employees:
            slip = compute_payslip(emp.basic_salary)
            Payslip.objects.create(
                run=run, employee=emp,
                gross=slip['gross'], nssf=slip['nssf'], nhif=slip['nhif'],
                paye=slip['paye'], net=slip['net'],
            )
            total_gross += slip['gross']
            total_net += slip['net']

        run.status = 'processed'
        run.total_gross = total_gross
        run.total_net = total_net
        run.save()
        return Response(PayrollRunSerializer(run).data)
