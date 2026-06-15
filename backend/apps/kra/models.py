from django.db import models
from decimal import Decimal
from uuid import uuid4

class KRATaxpayer(models.Model):
    """KRA Taxpayer Information"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.OneToOneField('core.Company', on_delete=models.CASCADE, related_name='kra_profile')
    
    # Taxpayer details
    pin = models.CharField(max_length=50)  # KRA PIN
    certificate_serial = models.CharField(max_length=100, blank=True)
    taxpayer_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True)
    
    # Tax obligations
    is_vat_registered = models.BooleanField(default=False)
    vat_registration_date = models.DateField(null=True, blank=True)
    vat_obligation_start = models.DateField(null=True, blank=True)
    
    is_income_tax_registered = models.BooleanField(default=True)
    is_withholding_tax_agent = models.BooleanField(default=False)
    withholding_tax_agent_number = models.CharField(max_length=50, blank=True)
    
    # Contact details on KRA
    kra_email = models.EmailField(blank=True)
    kra_phone = models.CharField(max_length=20, blank=True)
    kra_postal_address = models.CharField(max_length=255, blank=True)
    
    # API credentials
    kra_api_username = models.CharField(max_length=100, blank=True)
    kra_api_password = models.CharField(max_length=100, blank=True)
    kra_api_key = models.CharField(max_length=100, blank=True)
    
    # Certificates (stored as file paths)
    pin_certificate = models.FileField(upload_to='kra/certificates/', null=True, blank=True)
    vat_certificate = models.FileField(upload_to='kra/certificates/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.taxpayer_name} - {self.pin}"

class KRAPinValidation(models.Model):
    """Record of KRA PIN validation requests"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    
    # Request details
    pin_validated = models.CharField(max_length=50)
    request_date = models.DateTimeField(auto_now_add=True)
    
    # Response from KRA
    is_valid = models.BooleanField(default=False)
    taxpayer_name = models.CharField(max_length=255, blank=True)
    taxpayer_status = models.CharField(max_length=50, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    
    # Raw response
    raw_response = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.pin_validated} - {'Valid' if self.is_valid else 'Invalid'}"

class KRAVATReturn(models.Model):
    """KRA VAT Return submission record"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='kra_vat_returns')
    vat_return = models.ForeignKey('tax_kenya.VATReturn', on_delete=models.CASCADE)
    
    # Submission details
    submission_date = models.DateTimeField(auto_now_add=True)
    acknowledgement_receipt = models.CharField(max_length=100, blank=True)
    kra_status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted by KRA'),
        ('REJECTED', 'Rejected'),
        ('AMENDED', 'Amended'),
    ], default='PENDING')
    
    # Tax amounts submitted
    sales_vat_declared = models.DecimalField(max_digits=15, decimal_places=2)
    purchases_vat_declared = models.DecimalField(max_digits=15, decimal_places=2)
    net_vat_declared = models.DecimalField(max_digits=15, decimal_places=2)
    
    # KRA response
    kra_response_code = models.CharField(max_length=20, blank=True)
    kra_response_message = models.TextField(blank=True)
    kra_response_data = models.JSONField(default=dict, blank=True)
    
    # Payment
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"VAT Return {self.submission_date} - {self.kra_status}"

class KRAWithholdingTaxReturn(models.Model):
    """Withholding Tax return submission to KRA"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    
    # Period
    period_month = models.IntegerField()
    period_year = models.IntegerField()
    
    # Summary
    total_gross_payments = models.DecimalField(max_digits=15, decimal_places=2)
    total_tax_withheld = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Submission
    submission_date = models.DateTimeField(auto_now_add=True)
    acknowledgement_receipt = models.CharField(max_length=100, blank=True)
    kra_status = models.CharField(max_length=50, default='PENDING')
    
    # Detailed breakdown
    payees = models.JSONField(default=list)  # List of payee details
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WHT Return {self.period_month}/{self.period_year}"

class KRAeTIMSInvoice(models.Model):
    """eTIMS invoice for KRA electronic tax invoicing"""
    INVOICE_STATUS = [
        ('DRAFT', 'Draft'),
        ('VALIDATED', 'Validated by KRA'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.CASCADE, related_name='etims_records')
    
    # eTIMS specific fields
    etims_invoice_number = models.CharField(max_length=100, unique=True)
    qr_code = models.TextField(blank=True)  # Base64 or URL of QR code
    security_code = models.CharField(max_length=50, blank=True)
    
    # KRA validation
    kra_request_id = models.CharField(max_length=100, blank=True)
    kra_response_code = models.CharField(max_length=20, blank=True)
    kra_response_message = models.TextField(blank=True)
    validation_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='DRAFT')
    
    # Raw data
    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"eTIMS: {self.etims_invoice_number} - {self.status}"