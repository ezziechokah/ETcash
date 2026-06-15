from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from uuid import uuid4

class MpesaConfig(models.Model):
    """M-Pesa API Configuration for a business"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.OneToOneField('core.Company', on_delete=models.CASCADE, related_name='mpesa_config')
    
    # Paybill/Till details
    business_shortcode = models.CharField(max_length=20, help_text="M-Pesa Paybill or Till Number")
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=[('PAYBILL', 'Paybill'), ('TILL', 'Till Number')])
    
    # API Credentials (for production)
    consumer_key = models.CharField(max_length=100, blank=True)
    consumer_secret = models.CharField(max_length=100, blank=True)
    passkey = models.CharField(max_length=100, blank=True)
    
    # Environment
    environment = models.CharField(max_length=20, choices=[('SANDBOX', 'Sandbox'), ('PRODUCTION', 'Production')], default='SANDBOX')
    
    # Webhook endpoints
    confirmation_url = models.URLField(blank=True, help_text="URL for transaction confirmation")
    validation_url = models.URLField(blank=True, help_text="URL for transaction validation")
    result_url = models.URLField(blank=True, help_text="URL for result callback")
    
    # Auto reconciliation settings
    auto_reconcile = models.BooleanField(default=True, help_text="Automatically match payments to invoices")
    auto_send_stk = models.BooleanField(default=False, help_text="Automatically send STK push for invoices")
    
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
    
    TRANSACTION_TYPES = [
        ('PAYBILL', 'Paybill Payment'),
        ('TILL', 'Till Payment'),
        ('STK_PUSH', 'STK Push'),
        ('B2C', 'Business to Customer'),
        ('C2B', 'Customer to Business'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='mpesa_transactions')
    
    # Transaction identifiers
    transaction_id = models.CharField(max_length=50, unique=True, db_index=True, help_text="M-Pesa transaction ID (e.g., NFJ7KUJ6KL)")
    conversation_id = models.CharField(max_length=100, blank=True)
    originator_conversation_id = models.CharField(max_length=100, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='KES')
    
    # Customer details
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=20, db_index=True)
    customer_email = models.EmailField(blank=True)
    
    # Business details
    business_shortcode = models.CharField(max_length=20)
    account_reference = models.CharField(max_length=50, blank=True, db_index=True, help_text="Invoice number or account number")
    
    # Transaction metadata
    transaction_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, default='MPESA')
    receipt_number = models.CharField(max_length=50, blank=True)
    bill_ref_number = models.CharField(max_length=50, blank=True)
    
    # Linked records
    linked_invoice = models.ForeignKey('sales.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='mpesa_payments')
    linked_payment = models.ForeignKey('sales.Payment', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    failure_reason = models.TextField(blank=True)
    
    # STK Push specific fields
    checkout_request_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    customer_message = models.TextField(blank=True)
    
    # Raw data from API
    raw_callback_data = models.JSONField(default=dict, blank=True)
    raw_request_data = models.JSONField(default=dict, blank=True)
    
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
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.CASCADE, related_name='stk_pushes', null=True, blank=True)
    
    # Request details
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    account_reference = models.CharField(max_length=50)
    transaction_description = models.CharField(max_length=100)
    
    # M-Pesa identifiers
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100)
    response_code = models.CharField(max_length=10, blank=True)
    response_description = models.TextField(blank=True)
    
    # Customer response
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=255, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"STK Push for {self.phone_number} - KES {self.amount}"