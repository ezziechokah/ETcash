from decimal import Decimal

from django.db import models

from core.models import Company


class Account(models.Model):
    TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']
        unique_together = [['company', 'code']]

    def __str__(self):
        return f'{self.code} — {self.name}'


class JournalEntry(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('posted', 'Posted')]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='journal_entries')
    entry_date = models.DateField()
    reference = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date', '-id']
        verbose_name_plural = 'journal entries'

    def __str__(self):
        return self.reference or f'JE-{self.id}'


class JournalLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_lines')
    description = models.CharField(max_length=200, blank=True)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))

    class Meta:
        ordering = ['id']
