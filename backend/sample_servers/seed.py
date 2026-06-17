"""
Seed the local database with sample data from sample_servers.catalog.

Safe to run repeatedly — uses get_or_create / existence checks throughout.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounting.models import Account, JournalEntry, JournalLine
from accounting.seed import seed_chart_of_accounts
from banking.models import BankAccount, BankTransaction
from core.models import Company, UserProfile
from expenses.models import Bill, Expense, Vendor
from invoicing.models import Customer, Invoice, InvoiceLine
from invoicing.utils import compute_line_totals, next_invoice_number
from kra.models import KRATaxpayer
from mpesa.models import MpesaConfig, MpesaTransaction

from .catalog import (
    SAMPLE_ADMIN,
    SAMPLE_BANK_ACCOUNTS,
    SAMPLE_COMPANY,
    SAMPLE_CUSTOMERS,
    SAMPLE_EMPLOYEES,
    SAMPLE_INVENTORY,
    SAMPLE_KRA,
    SAMPLE_LEGAL_ENTITIES,
    SAMPLE_MPESA,
    SAMPLE_PROJECTS,
    SAMPLE_VENDORS,
)


def _ensure_company_and_admin():
    """Create demo company + admin user with profile if missing."""
    company = Company.objects.first()
    if not company:
        company = Company.objects.create(**SAMPLE_COMPANY)
        print(f'  Created company: {company.name}')
    else:
        print(f'  Using existing company: {company.name}')

    admin, created = User.objects.get_or_create(
        username=SAMPLE_ADMIN['username'],
        defaults={
            'email': SAMPLE_ADMIN['email'],
            'is_staff': True,
            'is_superuser': True,
        },
    )
    if created:
        admin.set_password(SAMPLE_ADMIN['password'])
        admin.save()
        print(f'  Created admin user: {SAMPLE_ADMIN["username"]}')
    else:
        print(f'  Admin user exists: {SAMPLE_ADMIN["username"]}')

    profile, profile_created = UserProfile.objects.get_or_create(
        user=admin,
        defaults={'company': company, 'full_name': SAMPLE_ADMIN['full_name']},
    )
    if not profile_created and profile.company_id != company.id:
        profile.company = company
        profile.save(update_fields=['company'])
        print('  Linked admin to company')

    Token.objects.get_or_create(user=admin)
    return company, admin


def _seed_customers(company):
    customers = []
    for data in SAMPLE_CUSTOMERS:
        customer, _ = Customer.objects.get_or_create(
            company=company,
            name=data['name'],
            defaults={
                'email': data.get('email', ''),
                'phone': data.get('phone', ''),
                'kra_pin': data.get('kra_pin', ''),
            },
        )
        customers.append(customer)
    print(f'  Customers: {len(customers)}')
    return customers


def _seed_vendors(company):
    vendors = []
    for data in SAMPLE_VENDORS:
        vendor, _ = Vendor.objects.get_or_create(
            company=company,
            name=data['name'],
            defaults={
                'email': data.get('email', ''),
                'phone': data.get('phone', ''),
                'kra_pin': data.get('kra_pin', ''),
            },
        )
        vendors.append(vendor)
    print(f'  Vendors: {len(vendors)}')
    return vendors


def _seed_invoices(company, customers):
    if Invoice.objects.filter(company=company).exists():
        print(f'  Invoices: {Invoice.objects.filter(company=company).count()} (existing)')
        return

    today = date.today()
    specs = [
        ('sent', customers[0], 'IT consulting (40 hrs)', Decimal('2'), Decimal('25000'), 30),
        ('paid', customers[1], 'Monthly retainer', Decimal('1'), Decimal('45000'), -15),
        ('sent', customers[2], 'Web development phase 1', Decimal('1'), Decimal('120000'), 14),
        ('draft', customers[3], 'Hardware supply', Decimal('5'), Decimal('18000'), 30),
        ('overdue', customers[4], 'Annual support contract', Decimal('1'), Decimal('96000'), -45),
    ]
    for status, customer, desc, qty, price, due_offset in specs:
        line_total, sub, tax = compute_line_totals(qty, price, Decimal('16'))
        inv = Invoice.objects.create(
            company=company,
            customer=customer,
            invoice_number=next_invoice_number(company),
            issue_date=today - timedelta(days=max(0, abs(due_offset))),
            due_date=today + timedelta(days=due_offset),
            status=status,
            subtotal=sub,
            tax_amount=tax,
            total_amount=line_total,
            notes=desc,
        )
        InvoiceLine.objects.create(
            invoice=inv,
            description=desc,
            quantity=qty,
            unit_price=price,
            tax_rate=Decimal('16'),
            line_total=line_total,
        )
    print(f'  Invoices: {Invoice.objects.filter(company=company).count()}')


def _seed_expenses(company, vendors):
    if Expense.objects.filter(company=company).count() >= 3:
        print(f'  Expenses: {Expense.objects.filter(company=company).count()} (existing)')
        return

    today = date.today()
    items = [
        (vendors[0], 'Office rent — VAT', 'Rent', Decimal('50000'), 16, 'bank_transfer', 'RENT-MAY'),
        (vendors[2], 'Legal services — WHT', 'Professional fees', Decimal('20000'), 5, 'mpesa', 'MPESA-LEGAL'),
        (vendors[1], 'Internet & telecom', 'Utilities', Decimal('8500'), 16, 'mpesa', 'TEL-JUN'),
        (vendors[0], 'Stationery supplies', 'Office supplies', Decimal('4500'), 16, 'cash', 'STAT-001'),
    ]
    for vendor, desc, category, amt, rate, method, ref in items:
        if Expense.objects.filter(company=company, description=desc).exists():
            continue
        tax = (amt * Decimal(rate) / 100).quantize(Decimal('0.01'))
        Expense.objects.create(
            company=company,
            vendor=vendor,
            expense_date=today - timedelta(days=random.randint(1, 60)),
            description=desc,
            category=category,
            amount=amt,
            tax_rate=rate,
            tax_amount=tax,
            total_amount=amt + tax,
            payment_method=method,
            reference=ref,
        )
    print(f'  Expenses: {Expense.objects.filter(company=company).count()}')


def _seed_bills(company, vendors):
    if Bill.objects.filter(company=company).exists():
        print(f'  Bills: {Bill.objects.filter(company=company).count()} (existing)')
        return

    today = date.today()
    amt = Decimal('35000')
    tax = (amt * Decimal('16') / 100).quantize(Decimal('0.01'))
    Bill.objects.create(
        company=company,
        vendor=vendors[0],
        bill_number='BILL-001',
        issue_date=today - timedelta(days=10),
        due_date=today + timedelta(days=20),
        status='open',
        subtotal=amt,
        tax_amount=tax,
        total_amount=amt + tax,
        notes='Q2 office supplies',
    )
    print('  Bills: 1')


def _seed_banking(company):
    for data in SAMPLE_BANK_ACCOUNTS:
        acct, created = BankAccount.objects.get_or_create(
            company=company,
            name=data['name'],
            defaults={
                'bank_name': data.get('bank_name', ''),
                'account_number': data.get('account_number', ''),
                'currency': data.get('currency', 'KES'),
                'opening_balance': Decimal(data['opening_balance']),
            },
        )
        if created and acct.name == 'Main Operating Account':
            today = date.today()
            txns = [
                (today - timedelta(days=5), 'Customer payment — Acme Kenya', 'CR-001', Decimal('58000'), 'credit'),
                (today - timedelta(days=3), 'Office rent', 'RENT-MAY', Decimal('58000'), 'debit'),
                (today - timedelta(days=1), 'M-Pesa collection', 'MPESA-BATCH', Decimal('125000'), 'credit'),
            ]
            for txn_date, desc, ref, amount, txn_type in txns:
                BankTransaction.objects.create(
                    account=acct,
                    transaction_date=txn_date,
                    description=desc,
                    reference=ref,
                    amount=amount,
                    txn_type=txn_type,
                )
    print(f'  Bank accounts: {BankAccount.objects.filter(company=company).count()}')


def _seed_journal(company):
    if JournalEntry.objects.filter(company=company, reference='DEMO-JE-001').exists():
        print('  Journal entries: existing')
        return

    seed_chart_of_accounts(company)
    cash = Account.objects.get(company=company, code='1000')
    sales = Account.objects.get(company=company, code='4000')
    entry = JournalEntry.objects.create(
        company=company,
        entry_date=date.today(),
        reference='DEMO-JE-001',
        description='Record cash sale',
        status='posted',
    )
    JournalLine.objects.create(entry=entry, account=cash, debit=Decimal('10000'), credit=0, description='Cash received')
    JournalLine.objects.create(entry=entry, account=sales, debit=0, credit=Decimal('10000'), description='Sales')
    print('  Journal: DEMO-JE-001 posted')


def _seed_inventory(company):
    from inventory.models import Item

    for data in SAMPLE_INVENTORY:
        Item.objects.get_or_create(
            company=company,
            sku=data['sku'],
            defaults={
                'name': data['name'],
                'quantity_on_hand': data['quantity_on_hand'],
                'unit_cost': Decimal(data['unit_cost']),
                'selling_price': Decimal(data['selling_price']),
                'reorder_level': data['reorder_level'],
            },
        )
    print(f'  Inventory items: {Item.objects.filter(company=company).count()}')


def _seed_payroll(company):
    from payroll.models import Employee

    for data in SAMPLE_EMPLOYEES:
        Employee.objects.get_or_create(
            company=company,
            employee_number=data['employee_number'],
            defaults={
                'full_name': data['full_name'],
                'basic_salary': Decimal(data['basic_salary']),
                'kra_pin': data.get('kra_pin', ''),
            },
        )
    print(f'  Employees: {Employee.objects.filter(company=company).count()}')


def _seed_projects(company):
    from projects.models import Project

    for data in SAMPLE_PROJECTS:
        Project.objects.get_or_create(
            company=company,
            code=data['code'],
            defaults={
                'name': data['name'],
                'client_name': data['client_name'],
                'budget': Decimal(data['budget']),
                'status': data['status'],
            },
        )
    print(f'  Projects: {Project.objects.filter(company=company).count()}')


def _seed_entities(company):
    if company.mode != 'multi_entity':
        return

    from entities.models import LegalEntity

    for data in SAMPLE_LEGAL_ENTITIES:
        LegalEntity.objects.get_or_create(
            company=company,
            code=data['code'],
            defaults={
                'name': data['name'],
                'kra_pin': data.get('kra_pin', ''),
                'is_default': data.get('is_default', False),
            },
        )
    print(f'  Legal entities: {LegalEntity.objects.filter(company=company).count()}')


def _seed_mpesa(company, customers):
    config, _ = MpesaConfig.objects.get_or_create(
        company=company,
        defaults=SAMPLE_MPESA,
    )

    if MpesaTransaction.objects.filter(company=company).count() >= 10:
        print(f'  M-Pesa transactions: {MpesaTransaction.objects.filter(company=company).count()} (existing)')
        return

    for i in range(15):
        customer = random.choice(customers) if customers else None
        transaction_id = f'SAMPLE{random.randint(100000000, 999999999)}'
        if MpesaTransaction.objects.filter(transaction_id=transaction_id).exists():
            continue
        amount = Decimal(random.randint(1000, 80000))
        days_ago = random.randint(0, 30)
        MpesaTransaction.objects.create(
            company=company,
            transaction_id=transaction_id,
            amount=amount,
            customer_phone=customer.phone.replace(' ', '').replace('+', '') if customer else f'2547{random.randint(10000000, 99999999)}',
            customer_name=customer.name if customer else f'Customer {i + 1}',
            business_shortcode=config.business_shortcode,
            account_reference=f'INV-{i + 1:03d}',
            transaction_date=timezone.now() - timedelta(days=days_ago, hours=random.randint(1, 12)),
            receipt_number=f'QK{random.randint(10000000, 99999999)}',
            status='COMPLETED',
        )
    print(f'  M-Pesa transactions: {MpesaTransaction.objects.filter(company=company).count()}')


def _seed_kra(company):
    KRATaxpayer.objects.get_or_create(
        company=company,
        defaults=SAMPLE_KRA,
    )
    print('  KRA taxpayer profile: configured')


def seed_all(*, verbose=True):
    """Run full sample environment seed. Returns (company, admin)."""
    if verbose:
        print('=' * 50)
        print('ETcash Sample Environment Seed')
        print('=' * 50)

    company, admin = _ensure_company_and_admin()
    seed_chart_of_accounts(company)

    customers = _seed_customers(company)
    vendors = _seed_vendors(company)
    _seed_invoices(company, customers)
    _seed_expenses(company, vendors)
    _seed_bills(company, vendors)
    _seed_banking(company)
    _seed_journal(company)

    if company.mode in ('sme', 'multi_entity'):
        _seed_inventory(company)
        _seed_payroll(company)
        _seed_projects(company)

    _seed_entities(company)
    _seed_mpesa(company, customers)
    _seed_kra(company)

    if verbose:
        inv_count = Invoice.objects.filter(company=company).count()
        exp_total = Expense.objects.filter(company=company).aggregate(t=Sum('total_amount'))['t'] or 0
        mpesa_total = MpesaTransaction.objects.filter(company=company, status='COMPLETED').aggregate(t=Sum('amount'))['t'] or 0
        print('')
        print('Sample environment ready:')
        print(f'  Login: {SAMPLE_ADMIN["username"]} / {SAMPLE_ADMIN["password"]}')
        print(f'  Company: {company.name} ({company.mode})')
        print(f'  Invoices: {inv_count} | Expenses total: KES {exp_total:,.2f}')
        print(f'  M-Pesa total: KES {mpesa_total:,.2f}')
        print('=' * 50)

    return company, admin
