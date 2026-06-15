from decimal import Decimal

from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import Account, JournalLine
from banking.models import BankAccount, BankTransaction
from expenses.models import Bill, Expense
from invoicing.models import Invoice


def _company(request):
    return request.user.profile.company


def _parse_period(request):
    start = parse_date(request.query_params.get('from', ''))
    end = parse_date(request.query_params.get('to', ''))
    as_of = parse_date(request.query_params.get('as_of', '')) or end
    return start, end, as_of


def _journal_lines(company, start=None, end=None, as_of=None):
    qs = JournalLine.objects.filter(entry__company=company, entry__status='posted')
    if start:
        qs = qs.filter(entry__entry_date__gte=start)
    if end:
        qs = qs.filter(entry__entry_date__lte=end)
    elif as_of:
        qs = qs.filter(entry__entry_date__lte=as_of)
    return qs


def _account_activity(company, account_type, start=None, end=None, as_of=None):
    lines = _journal_lines(company, start, end, as_of).filter(account__account_type=account_type)
    rows = []
    for account in Account.objects.filter(company=company, account_type=account_type, is_active=True):
        acc_lines = lines.filter(account=account)
        debit = acc_lines.aggregate(t=Sum('debit'))['t'] or Decimal('0')
        credit = acc_lines.aggregate(t=Sum('credit'))['t'] or Decimal('0')
        if account_type in ('asset', 'expense'):
            amount = debit - credit
        else:
            amount = credit - debit
        if amount != 0:
            rows.append({'code': account.code, 'name': account.name, 'amount': amount})
    return rows


class ProfitLossView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _company(request)
        start, end, _ = _parse_period(request)

        income = _account_activity(company, 'income', start, end)
        expenses_gl = _account_activity(company, 'expense', start, end)

        inv_qs = Invoice.objects.filter(company=company).exclude(status__in=['draft', 'void'])
        if start:
            inv_qs = inv_qs.filter(issue_date__gte=start)
        if end:
            inv_qs = inv_qs.filter(issue_date__lte=end)
        invoice_revenue = inv_qs.aggregate(t=Sum('subtotal'))['t'] or Decimal('0')
        if invoice_revenue:
            income.append({'code': 'SALES', 'name': 'Sales (invoices)', 'amount': invoice_revenue})

        exp_qs = Expense.objects.filter(company=company)
        if start:
            exp_qs = exp_qs.filter(expense_date__gte=start)
        if end:
            exp_qs = exp_qs.filter(expense_date__lte=end)
        expense_ops = exp_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        expense_items = list(expenses_gl)
        if expense_ops:
            expense_items.append({'code': 'EXP', 'name': 'Operating expenses (recorded)', 'amount': expense_ops})

        total_revenue = sum(i['amount'] for i in income)
        total_expenses = sum(e['amount'] for e in expense_items)
        net_profit = total_revenue - total_expenses

        return Response({
            'period': {'from': start, 'to': end},
            'revenue': income,
            'expenses': expense_items,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
        })


class BalanceSheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _company(request)
        _, _, as_of = _parse_period(request)

        assets = _account_activity(company, 'asset', as_of=as_of)
        liabilities = _account_activity(company, 'liability', as_of=as_of)
        equity = _account_activity(company, 'equity', as_of=as_of)

        ar = Invoice.objects.filter(company=company).exclude(
            status__in=['paid', 'void', 'draft']
        ).aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        if ar:
            assets.append({'code': 'AR', 'name': 'Accounts receivable (invoices)', 'amount': ar})

        for acct in BankAccount.objects.filter(company=company, is_active=True):
            credits = acct.transactions.filter(txn_type='credit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            debits = acct.transactions.filter(txn_type='debit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            bal = acct.opening_balance + credits - debits
            if bal:
                assets.append({'code': 'BANK', 'name': acct.name, 'amount': bal})

        ap = Bill.objects.filter(company=company, status='open').aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
        if ap:
            liabilities.append({'code': 'AP', 'name': 'Accounts payable (bills)', 'amount': ap})

        total_assets = sum(a['amount'] for a in assets)
        total_liabilities = sum(l['amount'] for l in liabilities)
        total_equity = sum(e['amount'] for e in equity)
        retained = total_assets - total_liabilities - total_equity
        if retained:
            equity.append({'code': 'RE', 'name': 'Retained earnings (computed)', 'amount': retained})
            total_equity += retained

        return Response({
            'as_of': as_of,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'balanced': abs(total_assets - total_liabilities - total_equity) < Decimal('0.01'),
        })


class CashFlowStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = _company(request)
        start, end, _ = _parse_period(request)

        inv_in = Invoice.objects.filter(company=company, status='paid')
        if start:
            inv_in = inv_in.filter(issue_date__gte=start)
        if end:
            inv_in = inv_in.filter(issue_date__lte=end)
        cash_from_sales = inv_in.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')

        sent_inv = Invoice.objects.filter(company=company, status='sent')
        if start:
            sent_inv = sent_inv.filter(issue_date__gte=start)
        if end:
            sent_inv = sent_inv.filter(issue_date__lte=end)
        expected_collections = sent_inv.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')

        exp_qs = Expense.objects.filter(company=company)
        if start:
            exp_qs = exp_qs.filter(expense_date__gte=start)
        if end:
            exp_qs = exp_qs.filter(expense_date__lte=end)
        cash_to_expenses = exp_qs.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')

        bank_in = Decimal('0')
        bank_out = Decimal('0')
        for acct in BankAccount.objects.filter(company=company):
            txns = acct.transactions.all()
            if start:
                txns = txns.filter(transaction_date__gte=start)
            if end:
                txns = txns.filter(transaction_date__lte=end)
            bank_in += txns.filter(txn_type='credit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            bank_out += txns.filter(txn_type='debit').aggregate(t=Sum('amount'))['t'] or Decimal('0')

        operating_in = cash_from_sales + bank_in
        operating_out = cash_to_expenses + bank_out
        net_operating = operating_in - operating_out

        return Response({
            'period': {'from': start, 'to': end},
            'operating': {
                'inflows': [
                    {'label': 'Cash from paid invoices', 'amount': cash_from_sales},
                    {'label': 'Bank deposits / credits', 'amount': bank_in},
                    {'label': 'Expected from sent invoices', 'amount': expected_collections},
                ],
                'outflows': [
                    {'label': 'Expenses paid', 'amount': cash_to_expenses},
                    {'label': 'Bank withdrawals / debits', 'amount': bank_out},
                ],
                'net': net_operating,
            },
            'net_change_in_cash': net_operating,
        })
