import requests
import json
from datetime import datetime
from django.conf import settings
from .models import WhatsAppMessage, WhatsAppConfig

class WhatsAppService:
    """WhatsApp Business API Integration"""
    
    def __init__(self, company):
        self.company = company
        self.config = company.whatsapp_config if hasattr(company, 'whatsapp_config') else None
        self.api_url = "https://graph.facebook.com/v18.0"
    
    def send_text_message(self, phone_number, text, invoice=None, customer=None):
        """Send a text message via WhatsApp"""
        
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        # Format phone number
        phone = self._format_phone(phone_number)
        
        # Prepare message
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }
        
        # For demo/sample, simulate sending
        if settings.DEBUG:
            import random
            import string
            
            message_id = f"whatsapp_{''.join(random.choices(string.digits, k=15))}"
            
            message = WhatsAppMessage.objects.create(
                company=self.company,
                phone_number=phone,
                contact_name=customer.name if customer else '',
                message_type='TEXT',
                content=text,
                direction='OUTBOUND',
                status='SENT',
                message_id=message_id,
                linked_invoice=invoice,
                linked_customer=customer,
                sent_at=datetime.now(),
                delivered_at=datetime.now()
            )
            
            return {
                'success': True,
                'message_id': message_id,
                'status': 'sent'
            }
        
        # Production API call
        """
        headers = {
            'Authorization': f'Bearer {self.config.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_url}/{self.config.phone_number_id}/messages"
        response = requests.post(url, json=message_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {'success': True, 'message_id': data.get('messages', [{}])[0].get('id')}
        """
        
        return {'success': False, 'error': 'WhatsApp service not available'}
    
    def send_template_message(self, phone_number, template_name, variables, invoice=None, customer=None):
        """Send a template message via WhatsApp"""
        
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        # Get template
        from .models import WhatsAppTemplate
        try:
            template = WhatsAppTemplate.objects.get(
                company=self.company,
                name=template_name,
                is_active=True
            )
        except WhatsAppTemplate.DoesNotExist:
            return {'success': False, 'error': f'Template {template_name} not found'}
        
        phone = self._format_phone(phone_number)
        
        # Prepare template message
        message_data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template.whatsapp_template_id or template_name,
                "language": {"code": template.language},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": str(variables.get(var, ''))}
                            for var in template.variables
                        ]
                    }
                ]
            }
        }
        
        # For demo, simulate
        if settings.DEBUG:
            import random
            import string
            
            rendered_content = template.render(variables)
            message_id = f"whatsapp_template_{''.join(random.choices(string.digits, k=15))}"
            
            message = WhatsAppMessage.objects.create(
                company=self.company,
                phone_number=phone,
                contact_name=customer.name if customer else '',
                message_type='TEMPLATE',
                content=rendered_content,
                direction='OUTBOUND',
                status='SENT',
                message_id=message_id,
                linked_invoice=invoice,
                linked_customer=customer,
                sent_at=datetime.now()
            )
            
            return {
                'success': True,
                'message_id': message_id,
                'rendered_content': rendered_content
            }
        
        return {'success': False, 'error': 'WhatsApp service not available'}
    
    def send_invoice(self, invoice):
        """Send invoice to customer via WhatsApp"""
        
        customer = invoice.customer
        phone = customer.phone
        
        if not phone:
            return {'success': False, 'error': 'Customer has no phone number'}
        
        # Format invoice data
        variables = {
            'customer_name': customer.name,
            'invoice_number': invoice.invoice_number,
            'amount': f"KES {invoice.total_amount:,.2f}",
            'due_date': invoice.due_date.strftime('%d/%m/%Y'),
            'link': f"https://pay.etcash.com/{invoice.id}"  # Payment link
        }
        
        # Send template message
        result = self.send_template_message(
            phone_number=phone,
            template_name='invoice_payment',
            variables=variables,
            invoice=invoice,
            customer=customer
        )
        
        # Auto-send STK push if configured
        if result.get('success') and hasattr(self.company, 'mpesa_config'):
            if self.company.mpesa_config.auto_send_stk:
                from apps.mpesa.services import MpesaService
                mpesa = MpesaService(self.company)
                mpesa.send_stk_push(
                    phone_number=phone,
                    amount=invoice.balance_due,
                    account_reference=invoice.invoice_number,
                    invoice=invoice
                )
        
        return result
    
    def send_payment_reminder(self, invoice):
        """Send payment reminder for overdue invoice"""
        
        customer = invoice.customer
        phone = customer.phone
        
        if not phone:
            return {'success': False, 'error': 'Customer has no phone number'}
        
        days_overdue = (datetime.now().date() - invoice.due_date).days
        
        variables = {
            'customer_name': customer.name,
            'invoice_number': invoice.invoice_number,
            'amount_due': f"KES {invoice.balance_due:,.2f}",
            'days_overdue': str(days_overdue),
            'link': f"https://pay.etcash.com/{invoice.id}"
        }
        
        return self.send_template_message(
            phone_number=phone,
            template_name='payment_reminder',
            variables=variables,
            invoice=invoice,
            customer=customer
        )
    
    def send_payment_receipt(self, payment):
        """Send payment receipt via WhatsApp"""
        
        invoice = payment.invoice
        customer = invoice.customer
        
        variables = {
            'customer_name': customer.name,
            'invoice_number': invoice.invoice_number,
            'amount_paid': f"KES {payment.amount:,.2f}",
            'balance': f"KES {invoice.balance_due:,.2f}",
            'payment_date': payment.payment_date.strftime('%d/%m/%Y'),
            'mpesa_code': payment.reference_number
        }
        
        return self.send_template_message(
            phone_number=customer.phone,
            template_name='payment_receipt',
            variables=variables,
            invoice=invoice,
            customer=customer
        )
    
    def send_bulk_reminders(self):
        """Send payment reminders to all overdue invoices"""
        
        from apps.sales.models import Invoice
        from datetime import date
        
        overdue_invoices = Invoice.objects.filter(
            company=self.company,
            due_date__lt=date.today(),
            status__in=['SENT', 'PARTIAL']
        )
        
        results = []
        for invoice in overdue_invoices:
            if invoice.customer.phone:
                result = self.send_payment_reminder(invoice)
                results.append({
                    'invoice': invoice.invoice_number,
                    'success': result.get('success', False)
                })
        
        return results
    
    def _format_phone(self, phone_number):
        """Format phone number for WhatsApp API"""
        phone = phone_number.strip()
        
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Ensure it starts with 254
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('254'):
            pass
        else:
            phone = '254' + phone
        
        return phone