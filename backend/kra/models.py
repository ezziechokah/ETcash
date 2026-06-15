from django.db import models
from uuid import uuid4

class KRATaxpayer(models.Model):
    """KRA Taxpayer Information"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.OneToOneField('core.Company', on_delete=models.CASCADE, related_name='kra_profile')
    
    pin = models.CharField(max_length=50)
    taxpayer_name = models.CharField(max_length=255)
    is_vat_registered = models.BooleanField(default=False)
    vat_registration_date = models.DateField(null=True, blank=True)
    
    is_withholding_tax_agent = models.BooleanField(default=False)
    withholding_tax_agent_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.taxpayer_name} - {self.pin}"

class KRAPinValidation(models.Model):
    """Record of KRA PIN validation requests"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    
    pin_validated = models.CharField(max_length=50)
    is_valid = models.BooleanField(default=False)
    taxpayer_name = models.CharField(max_length=255, blank=True)
    response_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.pin_validated} - {'Valid' if self.is_valid else 'Invalid'}"

class KRAVATReturn(models.Model):
    """KRA VAT Return submission record - Simplified"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    sales_vat_declared = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    purchases_vat_declared = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_vat_declared = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    submission_date = models.DateTimeField(auto_now_add=True)
    acknowledgement_receipt = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default='PENDING')
    
    def __str__(self):
        return f"VAT Return {self.period_start} to {self.period_end}"

class KRAeTIMSInvoice(models.Model):
    """eTIMS invoice for KRA electronic tax invoicing"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    
    invoice_number = models.CharField(max_length=50)
    etims_invoice_number = models.CharField(max_length=100, unique=True)
    qr_code = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"eTIMS: {self.etims_invoice_number}"