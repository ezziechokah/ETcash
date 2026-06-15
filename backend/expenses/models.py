from django.db import models

from core.models import Company


class Vendor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vendors')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    kra_pin = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    expense_date = models.DateField()
    description = models.CharField(max_length=300)
    category = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_method = models.CharField(max_length=30, default='bank_transfer')
    reference = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-id']

    @property
    def vendor_name(self):
        return self.vendor.name if self.vendor else ''


class Bill(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bills')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills')
    bill_number = models.CharField(max_length=30)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['company', 'bill_number']]

    @property
    def vendor_name(self):
        return self.vendor.name
