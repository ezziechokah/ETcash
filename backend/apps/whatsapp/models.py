from django.db import models
from uuid import uuid4

class WhatsAppConfig(models.Model):
    """WhatsApp Business API Configuration"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.OneToOneField('core.Company', on_delete=models.CASCADE, related_name='whatsapp_config')
    
    phone_number_id = models.CharField(max_length=100)
    business_account_id = models.CharField(max_length=100, blank=True)
    access_token = models.CharField(max_length=500)
    
    webhook_verify_token = models.CharField(max_length=100, blank=True)
    webhook_url = models.URLField(blank=True)
    
    invoice_template_name = models.CharField(max_length=100, default='invoice_payment')
    reminder_template_name = models.CharField(max_length=100, default='payment_reminder')
    receipt_template_name = models.CharField(max_length=100, default='payment_receipt')
    
    auto_send_invoice = models.BooleanField(default=False)
    auto_send_reminders = models.BooleanField(default=False)
    reminder_days_before_due = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"WhatsApp Config for {self.company.name}"

class WhatsAppMessage(models.Model):
    """Record of WhatsApp messages sent/received"""
    DIRECTION_CHOICES = [
        ('OUTBOUND', 'Outbound'),
        ('INBOUND', 'Inbound'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='whatsapp_messages')
    
    phone_number = models.CharField(max_length=20, db_index=True)
    contact_name = models.CharField(max_length=255, blank=True)
    
    message_type = models.CharField(max_length=50, choices=[
        ('TEXT', 'Text'),
        ('DOCUMENT', 'Document'),
        ('TEMPLATE', 'Template'),
        ('INTERACTIVE', 'Interactive'),
    ])
    content = models.TextField()
    media_url = models.URLField(blank=True)
    
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    message_id = models.CharField(max_length=100, unique=True, db_index=True)
    conversation_id = models.CharField(max_length=100, blank=True)
    
    # Store IDs as strings to avoid foreign key issues
    linked_invoice_id = models.CharField(max_length=100, blank=True, db_index=True)
    linked_customer_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    error_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['linked_invoice_id']),
        ]
    
    def __str__(self):
        return f"{self.direction} - {self.phone_number} - {self.message_type}"

class WhatsAppTemplate(models.Model):
    """WhatsApp message templates"""
    CATEGORY_CHOICES = [
        ('INVOICE', 'Invoice'),
        ('PAYMENT_REMINDER', 'Payment Reminder'),
        ('RECEIPT', 'Receipt'),
        ('STATEMENT', 'Statement'),
        ('MARKETING', 'Marketing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='whatsapp_templates')
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    language = models.CharField(max_length=10, default='en')
    content = models.TextField(help_text="Use {{variable_name}} for dynamic content")
    
    variables = models.JSONField(default=list, help_text="List of variable names used in template")
    
    whatsapp_template_id = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.language})"
    
    def render(self, context):
        """Render template with context variables"""
        rendered = self.content
        for var in self.variables:
            value = context.get(var, f'{{{{{var}}}}}')
            rendered = rendered.replace(f'{{{{{var}}}}}', str(value))
        return rendered