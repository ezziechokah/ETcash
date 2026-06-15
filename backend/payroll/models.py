from decimal import Decimal

from django.db import models

from core.models import Company


class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    employee_number = models.CharField(max_length=30)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    nssf_number = models.CharField(max_length=30, blank=True)
    nhif_number = models.CharField(max_length=30, blank=True)
    basic_salary = models.DecimalField(max_digits=14, decimal_places=2)
    bank_account = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['company', 'employee_number']]
        ordering = ['full_name']


class PayrollRun(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('processed', 'Processed'), ('paid', 'Paid')]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payroll_runs')
    period_month = models.PositiveSmallIntegerField()
    period_year = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['company', 'period_month', 'period_year']]
        ordering = ['-period_year', '-period_month']


class Payslip(models.Model):
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payslips')
    gross = models.DecimalField(max_digits=14, decimal_places=2)
    nssf = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    nhif = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    paye = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    net = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        unique_together = [['run', 'employee']]

    @property
    def employee_name(self):
        return self.employee.full_name
