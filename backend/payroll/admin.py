from django.contrib import admin

from .models import Employee, PayrollRun, Payslip

admin.site.register(Employee)
admin.site.register(PayrollRun)
admin.site.register(Payslip)
