from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from expenses.models import Expense
from inventory.models import Item
from invoicing.models import Invoice


def generate_insights(company):
    today = timezone.now().date()
    insights = []

    overdue = Invoice.objects.filter(
        company=company, due_date__lt=today
    ).exclude(status__in=['paid', 'void', 'draft'])
    overdue_amt = overdue.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    if overdue.count():
        insights.append({
            'severity': 'danger',
            'title': f'{overdue.count()} overdue invoice(s)',
            'message': f'KES {overdue_amt:,.2f} past due — chase customers to improve cash flow.',
        })

    sent_ar = Invoice.objects.filter(company=company, status='sent').aggregate(
        t=Sum('total_amount')
    )['t'] or Decimal('0')
    if sent_ar > 0:
        insights.append({
            'severity': 'warning',
            'title': 'Outstanding sent invoices',
            'message': f'KES {sent_ar:,.2f} invoiced but not yet marked paid.',
        })

    low_stock = Item.objects.filter(
        company=company, is_active=True, reorder_level__gt=0
    ).filter(quantity_on_hand__lte=F('reorder_level'))
    if low_stock.exists():
        insights.append({
            'severity': 'warning',
            'title': 'Low stock alert',
            'message': f'{low_stock.count()} item(s) at or below reorder level.',
        })

    month_start = today.replace(day=1)
    mtd_exp = Expense.objects.filter(
        company=company, expense_date__gte=month_start
    ).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
    mtd_rev = Invoice.objects.filter(
        company=company, issue_date__gte=month_start
    ).exclude(status__in=['draft', 'void']).aggregate(t=Sum('subtotal'))['t'] or Decimal('0')
    if mtd_exp > mtd_rev and mtd_exp > 0:
        insights.append({
            'severity': 'danger',
            'title': 'Expenses exceed revenue (MTD)',
            'message': f'Spent KES {mtd_exp:,.2f} vs revenue KES {mtd_rev:,.2f} this month.',
        })
    elif mtd_rev > 0:
        insights.append({
            'severity': 'success',
            'title': 'Positive revenue month',
            'message': f'MTD revenue KES {mtd_rev:,.2f} — keep monitoring margins.',
        })

    if Expense.objects.filter(company=company, tax_rate=16, expense_date__gte=month_start).exists():
        insights.append({
            'severity': 'info',
            'title': 'VAT input available',
            'message': 'Claim VAT on qualifying purchases when filing your KRA return.',
        })

    if not insights:
        insights.append({
            'severity': 'info',
            'title': 'Getting started',
            'message': 'Add invoices, expenses, and payroll to unlock more insights.',
        })

    return insights
