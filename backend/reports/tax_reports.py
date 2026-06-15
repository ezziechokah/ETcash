from decimal import Decimal

from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from expenses.models import Expense
from invoicing.models import Invoice


def _parse_range(request):
    start = parse_date(request.query_params.get('from', ''))
    end = parse_date(request.query_params.get('to', ''))
    return start, end


def _in_range(qs, field, start, end):
    if start:
        qs = qs.filter(**{f'{field}__gte': start})
    if end:
        qs = qs.filter(**{f'{field}__lte': end})
    return qs


class VatReportView(APIView):
    """Kenya VAT 16% — output from sales, input from purchases."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.profile.company
        start, end = _parse_range(request)

        invoices = _in_range(
            Invoice.objects.filter(company=company).exclude(status__in=['draft', 'void']),
            'issue_date', start, end,
        )
        output_vat = invoices.aggregate(t=Sum('tax_amount'))['t'] or Decimal('0')
        taxable_sales = invoices.aggregate(t=Sum('subtotal'))['t'] or Decimal('0')

        expenses = _in_range(
            Expense.objects.filter(company=company, tax_rate=16),
            'expense_date', start, end,
        )
        input_vat = expenses.aggregate(t=Sum('tax_amount'))['t'] or Decimal('0')
        taxable_purchases = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')

        net_vat = output_vat - input_vat

        return Response({
            'period': {'from': start, 'to': end},
            'vat_rate': 16,
            'output': {
                'taxable_amount': taxable_sales,
                'vat_amount': output_vat,
                'invoice_count': invoices.count(),
            },
            'input': {
                'taxable_amount': taxable_purchases,
                'vat_amount': input_vat,
                'expense_count': expenses.count(),
            },
            'net_vat_payable': net_vat,
            'line_items': [
                {
                    'type': 'output',
                    'label': 'VAT on sales (16%)',
                    'base': str(taxable_sales),
                    'tax': str(output_vat),
                },
                {
                    'type': 'input',
                    'label': 'VAT on purchases (16%)',
                    'base': str(taxable_purchases),
                    'tax': str(input_vat),
                },
            ],
        })


class WhtReportView(APIView):
    """Kenya WHT — 3% goods, 5% services, 10% rent."""
    permission_classes = [IsAuthenticated]

    WHT_RATES = {
        Decimal('3'): 'WHT 3% (Goods)',
        Decimal('5'): 'WHT 5% (Services)',
        Decimal('10'): 'WHT 10% (Rent)',
    }

    def get(self, request):
        company = request.user.profile.company
        start, end = _parse_range(request)

        expenses = _in_range(Expense.objects.filter(company=company), 'expense_date', start, end)
        expenses = expenses.filter(tax_rate__in=self.WHT_RATES.keys())

        breakdown = []
        total_wht = Decimal('0')
        for rate, label in self.WHT_RATES.items():
            qs = expenses.filter(tax_rate=rate)
            wht = qs.aggregate(t=Sum('tax_amount'))['t'] or Decimal('0')
            base = qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
            total_wht += wht
            breakdown.append({
                'rate': float(rate),
                'label': label,
                'gross_amount': base,
                'wht_amount': wht,
                'count': qs.count(),
            })

        return Response({
            'period': {'from': start, 'to': end},
            'total_wht': total_wht,
            'breakdown': breakdown,
        })
