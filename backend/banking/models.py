from decimal import Decimal

from django.db import models

from core.models import Company


class BankAccount(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=120)
    bank_name = models.CharField(max_length=120, blank=True)
    account_number = models.CharField(max_length=40, blank=True)
    currency = models.CharField(max_length=3, default='KES')
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BankTransaction(models.Model):
    TYPE_CHOICES = [('debit', 'Debit'), ('credit', 'Credit')]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateField()
    description = models.CharField(max_length=300)
    reference = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    txn_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reconciled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date', '-id']
