from django.db import models
from django.core.validators import MinValueValidator
from uuid import uuid4

class MpesaConfig(models.Model):
    """M-Pesa API Configuration for a business"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.OneToOneField('core.Company', on_delete=models.CASCADE, related_name='mpesa_config')
    
    business_shortcode = models.CharField(max_length=20, help_text="M-Pesa Paybill or Till Number")
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=[('PAYBILL', 'Paybill'), ('TILL', 'Till Number')])
    
    consumer_key = models.CharField(max_length=100, blank=True)
    consumer_secret = models.CharField(max_length=100, blank=True)
    passkey = models.CharField(max_length=100, blank=True)
    
    environment = models.CharField(max_length=20, choices=[('SANDBOX', 'Sandbox'), ('PRODUCTION', 'Production')], default='SANDBOX')
    
    confirmation_url = models.URLField(blank=True)
    validation_url = models.URLField(blank=True)
    result_url = models.URLField(blank=True)
    
    auto_reconcile = models.BooleanField(default=True)
    auto_send_stk = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} - {self.business_shortcode}"

class MpesaTransaction(models.Model):
    """Record of all M-Pesa transactions"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='mpesa_transactions')
    
    transaction_id = models.CharField(max_length=50, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='KES')
    
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=20, db_index=True)
    
    business_shortcode = models.CharField(max_length=20)
    account_reference = models.CharField(max_length=50, blank=True, db_index=True)
    
    transaction_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, default='MPESA')
    receipt_number = models.CharField(max_length=50, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    failure_reason = models.TextField(blank=True)
    
    # Store invoice reference as string to avoid foreign key issues
    invoice_reference = models.CharField(max_length=50, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['customer_phone']),
            models.Index(fields=['account_reference']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.customer_phone} - KES {self.amount}"

class MpesaSTKPush(models.Model):
    """Record of STK Push requests sent to customers"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('TIMEOUT', 'Timeout'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='stk_pushes')
    
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    account_reference = models.CharField(max_length=50)
    transaction_description = models.CharField(max_length=100)
    
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"STK Push for {self.phone_number} - KES {self.amount}"