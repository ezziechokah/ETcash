from datetime import date
from decimal import Decimal

from .models import Invoice


def next_invoice_number(company):
    year = date.today().year
    prefix = f'INV-{year}-'
    last = (
        Invoice.objects.filter(company=company, invoice_number__startswith=prefix)
        .order_by('-invoice_number')
        .first()
    )
    if last:
        try:
            seq = int(last.invoice_number.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'


def compute_line_totals(quantity, unit_price, tax_rate):
    subtotal = (quantity * unit_price).quantize(Decimal('0.01'))
    tax = (subtotal * tax_rate / Decimal('100')).quantize(Decimal('0.01'))
    return subtotal + tax, subtotal, tax
