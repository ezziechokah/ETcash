"""
Run end-to-end demo: customer, invoice, expenses, journal, tax reports.
Usage: python scripts/seed_demo_flow.py
"""
import os
import sys
from datetime import date
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etcash.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from accounting.models import Account, JournalEntry, JournalLine
from accounting.seed import seed_chart_of_accounts
from core.models import Company
from expenses.models import Expense, Vendor
from invoicing.models import Customer, Invoice, InvoiceLine
from invoicing.utils import compute_line_totals, next_invoice_number


def main():
    user = User.objects.filter(username='admin').first()
    if not user or not hasattr(user, 'profile'):
        print('No admin user — run setup in the app first.')
        return 1
    company = user.profile.company
    token, _ = Token.objects.get_or_create(user=user)
    print(f'Company: {company.name} | Token: {token.key[:12]}...')

    seed_chart_of_accounts(company)

    customer, _ = Customer.objects.get_or_create(
        company=company, name='Acme Kenya Ltd',
        defaults={'email': 'billing@acme.co.ke', 'phone': '+254 700 123456', 'kra_pin': 'P051234567X'},
    )
    print(f'Customer: {customer.name}')

    inv = Invoice.objects.filter(company=company, customer=customer, status='sent').first()
    if not inv:
        qty, price, rate = Decimal('2'), Decimal('25000'), Decimal('16')
        line_total, sub, tax = compute_line_totals(qty, price, rate)
        inv = Invoice.objects.create(
            company=company,
            customer=customer,
            invoice_number=next_invoice_number(company),
            issue_date=date.today(),
            due_date=date.today(),
            status='sent',
            subtotal=sub,
            tax_amount=tax,
            total_amount=line_total,
            notes='Consulting services — Q2',
        )
        InvoiceLine.objects.create(
            invoice=inv, description='IT consulting (40 hrs)', quantity=qty,
            unit_price=price, tax_rate=rate, line_total=line_total,
        )
    print(f'Invoice: {inv.invoice_number} status={inv.status} total={inv.total_amount}')

    vendor, _ = Vendor.objects.get_or_create(
        company=company, name='Office Supplies Kenya',
        defaults={'kra_pin': 'P059999999X'},
    )

    if not Expense.objects.filter(company=company, description='Office rent — VAT').exists():
        amt = Decimal('50000')
        tax = (amt * Decimal('16') / 100).quantize(Decimal('0.01'))
        Expense.objects.create(
            company=company, vendor=vendor, expense_date=date.today(),
            description='Office rent — VAT', category='Rent', amount=amt,
            tax_rate=16, tax_amount=tax, total_amount=amt + tax,
            payment_method='bank_transfer', reference='RENT-MAY',
        )
        print('Expense: Office rent (VAT 16%)')

    if not Expense.objects.filter(company=company, description='Legal services — WHT').exists():
        amt = Decimal('20000')
        tax = (amt * Decimal('5') / 100).quantize(Decimal('0.01'))
        Expense.objects.create(
            company=company, vendor=vendor, expense_date=date.today(),
            description='Legal services — WHT', category='Professional fees', amount=amt,
            tax_rate=5, tax_amount=tax, total_amount=amt + tax,
            payment_method='mpesa', reference='MPESA-LEGAL',
        )
        print('Expense: Legal services (WHT 5%)')

    if not JournalEntry.objects.filter(company=company, reference='DEMO-JE-001').exists():
        cash = Account.objects.get(company=company, code='1000')
        sales = Account.objects.get(company=company, code='4000')
        entry = JournalEntry.objects.create(
            company=company, entry_date=date.today(), reference='DEMO-JE-001',
            description='Record cash sale', status='posted',
        )
        JournalLine.objects.create(entry=entry, account=cash, debit=Decimal('10000'), credit=0, description='Cash received')
        JournalLine.objects.create(entry=entry, account=sales, debit=0, credit=Decimal('10000'), description='Sales')
        print('Journal: DEMO-JE-001 posted')

    y = date.today().year
    from reports.financial_reports import BalanceSheetView, CashFlowStatementView, ProfitLossView
    from reports.tax_reports import VatReportView, WhtReportView

    class Req:
        pass

    req = Req()
    req.user = user
    req.query_params = {'from': f'{y}-01-01', 'to': f'{y}-12-31', 'as_of': date.today().isoformat()}

    pl = ProfitLossView().get(req).data
    print(f"P&L: revenue={pl['total_revenue']} expenses={pl['total_expenses']} net={pl['net_profit']}")

    vat = VatReportView().get(req).data
    print(f"VAT: output={vat['output']['vat_amount']} input={vat['input']['vat_amount']} net={vat['net_vat_payable']}")

    wht = WhtReportView().get(req).data
    print(f"WHT total: {wht['total_wht']}")

    cf = CashFlowStatementView().get(req).data
    print(f"Cash flow net: {cf['net_change_in_cash']}")

    from inventory.models import Item
    from payroll.models import Employee
    from projects.models import Project

    Item.objects.get_or_create(company=company, sku='SKU-001', defaults={
        'name': 'Network Switch 24-port', 'quantity_on_hand': 5, 'unit_cost': 12000,
        'selling_price': 18000, 'reorder_level': 2,
    })
    Employee.objects.get_or_create(company=company, employee_number='EMP-001', defaults={
        'full_name': 'Jane Wanjiku', 'basic_salary': 85000, 'kra_pin': 'A001234567B',
    })
    Project.objects.get_or_create(company=company, code='PRJ-001', defaults={
        'name': 'Nairobi Office Fit-out', 'client_name': 'Acme Kenya Ltd', 'budget': 500000,
        'status': 'in_progress',
    })
    print('Also seeded: inventory item, employee, project.')

    print('\nDemo data ready. Open http://localhost:5173 and sign in as admin.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
