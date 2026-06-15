from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from banking.models import BankAccount
from expenses.models import Bill, Expense
from invoicing.models import Invoice


def _company(request):
    return request.user.profile.company


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _company(request)
        invoices = Invoice.objects.filter(company=company)
        today = timezone.now().date()

        total_ar = invoices.exclude(status__in=['paid', 'void']).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')

        overdue_qs = invoices.filter(due_date__lt=today).exclude(status__in=['paid', 'void'])
        overdue_count = overdue_qs.count()
        overdue_amount = overdue_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        total_ap = Bill.objects.filter(company=company, status='open').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')

        cash_position = Decimal('0')
        for acct in BankAccount.objects.filter(company=company, is_active=True):
            credits = acct.transactions.filter(txn_type='credit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            debits = acct.transactions.filter(txn_type='debit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            cash_position += acct.opening_balance + credits - debits

        month_start = today.replace(day=1)
        mtd_revenue = invoices.filter(issue_date__gte=month_start).exclude(
            status__in=['draft', 'void']
        ).aggregate(t=Sum('subtotal'))['t'] or Decimal('0')
        mtd_expenses = Expense.objects.filter(company=company, expense_date__gte=month_start).aggregate(
            t=Sum('total_amount')
        )['t'] or Decimal('0')
        net_profit_mtd = mtd_revenue - mtd_expenses

        expense_breakdown = list(
            Expense.objects.filter(company=company, expense_date__gte=month_start)
            .values('category')
            .annotate(amount=Sum('total_amount'))
            .order_by('-amount')[:6]
        )
        for row in expense_breakdown:
            row['category'] = row['category'] or 'Uncategorized'

        return Response({
            'cash_position': cash_position,
            'cash_trend': 0,
            'total_ar': total_ar,
            'ar_trend': 0,
            'total_ap': total_ap,
            'ap_trend': 0,
            'net_profit_mtd': net_profit_mtd,
            'profit_trend': 0,
            'expense_breakdown': expense_breakdown,
            'overdue_invoices': overdue_count,
            'overdue_amount': overdue_amount,
        })


class CashflowChartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _company(request)
        today = timezone.now().date()
        months = []
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            m_start = date(y, m, 1)
            days = 28 if m == 2 else (30 if m in (4, 6, 9, 11) else 31)
            m_end = date(y, m, days)
            inflow = Invoice.objects.filter(
                company=company, issue_date__gte=m_start, issue_date__lte=m_end
            ).exclude(status__in=['draft', 'void']).aggregate(t=Sum('total_amount'))['t'] or 0
            outflow = Expense.objects.filter(
                company=company, expense_date__gte=m_start, expense_date__lte=m_end
            ).aggregate(t=Sum('total_amount'))['t'] or 0
            months.append({
                'month': date(y, m, 1).strftime('%b'),
                'inflow': float(inflow),
                'outflow': float(outflow),
            })
        return Response({'monthly': months})


class TaxInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .insights import generate_insights
        company = _company(request)
        return Response({'insights': generate_insights(company)})
