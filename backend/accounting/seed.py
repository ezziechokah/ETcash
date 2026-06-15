from .models import Account

DEFAULT_ACCOUNTS = [
    ('1000', 'Cash on Hand', 'asset'),
    ('1010', 'Bank Account', 'asset'),
    ('1100', 'Accounts Receivable', 'asset'),
    ('1200', 'VAT Input (Recoverable)', 'asset'),
    ('2000', 'Accounts Payable', 'liability'),
    ('2100', 'VAT Output (Payable)', 'liability'),
    ('2200', 'Withholding Tax Payable', 'liability'),
    ('3000', "Owner's Equity", 'equity'),
    ('4000', 'Sales Revenue', 'income'),
    ('4100', 'Other Income', 'income'),
    ('5000', 'Cost of Goods Sold', 'expense'),
    ('5100', 'Operating Expenses', 'expense'),
    ('5200', 'Payroll Expense', 'expense'),
    ('5300', 'Bank Charges', 'expense'),
]


def seed_chart_of_accounts(company):
    if Account.objects.filter(company=company).exists():
        return
    Account.objects.bulk_create([
        Account(company=company, code=code, name=name, account_type=atype)
        for code, name, atype in DEFAULT_ACCOUNTS
    ])
