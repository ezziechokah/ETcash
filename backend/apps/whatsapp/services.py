import json
from datetime import datetime
from django.conf import settings
from .models import WhatsAppMessage, WhatsAppConfig, WhatsAppTemplate

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
        
        phone = self._format_phone(phone_number)
        
        if settings.DEBUG:
            import random
            import string
            
            message_id = f"whatsapp_{''.join(random.choices(string.digits, k=15))}"
            
            message_data = {
                'company': self.company,
                'phone_number': phone,
                'message_type': 'TEXT',
                'content': text,
                'direction': 'OUTBOUND',
                'status': 'SENT',
                'message_id': message_id,
                'sent_at': datetime.now(),
                'delivered_at': datetime.now()
            }
            
            if customer:
                message_data['contact_name'] = customer.name if hasattr(customer, 'name') else ''
                message_data['linked_customer_id'] = customer.id if hasattr(customer, 'id') else None
            
            if invoice:
                message_data['linked_invoice_id'] = invoice.id if hasattr(invoice, 'id') else None
            
            message = WhatsAppMessage.objects.create(**message_data)
            
            return {
                'success': True,
                'message_id': message_id,
                'status': 'sent'
            }
        
        return {'success': False, 'error': 'WhatsApp service not available'}
    
    def send_template_message(self, phone_number, template_name, variables, invoice=None, customer=None):
        """Send a template message via WhatsApp"""
        
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        try:
            template = WhatsAppTemplate.objects.get(
                company=self.company,
                name=template_name,
                is_active=True
            )
        except WhatsAppTemplate.DoesNotExist:
            return {'success': False, 'error': f'Template {template_name} not found'}
        
        phone = self._format_phone(phone_number)
        
        if settings.DEBUG:
            import random
            import string
            
            rendered_content = template.render(variables)
            message_id = f"whatsapp_template_{''.join(random.choices(string.digits, k=15))}"
            
            message_data = {
                'company': self.company,
                'phone_number': phone,
                'message_type': 'TEMPLATE',
                'content': rendered_content,
                'direction': 'OUTBOUND',
                'status': 'SENT',
                'message_id': message_id,
                'sent_at': datetime.now()
            }
            
            if customer:
                message_data['contact_name'] = customer.name if hasattr(customer, 'name') else ''
                message_data['linked_customer_id'] = customer.id if hasattr(customer, 'id') else None
            
            if invoice:
                message_data['linked_invoice_id'] = invoice.id if hasattr(invoice, 'id') else None
            
            message = WhatsAppMessage.objects.create(**message_data)
            
            return {
                'success': True,
                'message_id': message_id,
                'rendered_content': rendered_content
            }
        
        return {'success': False, 'error': 'WhatsApp service not available'}
    
    def send_invoice(self, invoice):
        """Send invoice to customer via WhatsApp"""
        
        # Get customer from invoice
        customer = None
        if hasattr(invoice, 'customer'):
            customer = invoice.customer
        
        if not customer:
            return {'success': False, 'error': 'Invoice has no customer'}
        
        phone = getattr(customer, 'phone', None)
        if not phone:
            return {'success': False, 'error': 'Customer has no phone number'}
        
        customer_name = getattr(customer, 'name', 'Customer')
        invoice_number = getattr(invoice, 'invoice_number', 'N/A')
        total_amount = float(getattr(invoice, 'total_amount', 0))
        due_date = getattr(invoice, 'due_date', datetime.now().date())
        invoice_id = getattr(invoice, 'id', '')
        
        variables = {
            'customer_name': customer_name,
            'invoice_number': invoice_number,
            'amount': f"KES {total_amount:,.2f}",
            'due_date': due_date.strftime('%d/%m/%Y'),
            'link': f"https://pay.etcash.com/{invoice_id}"
        }
        
        result = self.send_template_message(
            phone_number=phone,
            template_name='invoice_payment',
            variables=variables,
            invoice=invoice,
            customer=customer
        )
        
        # Auto-send STK push if configured (check for mpesa_config attribute)
        if result.get('success') and hasattr(self.company, 'mpesa_config'):
            mpesa_config = self.company.mpesa_config
            if hasattr(mpesa_config, 'auto_send_stk') and mpesa_config.auto_send_stk:
                try:
                    # Try to import MpesaService dynamically to avoid circular imports
                    from importlib import import_module
                    MpesaService = getattr(import_module('mpesa.services'), 'MpesaService', None)
                    if MpesaService:
                        mpesa = MpesaService(self.company)
                        balance_due = float(getattr(invoice, 'balance_due', total_amount))
                        mpesa.send_stk_push(
                            phone_number=phone,
                            amount=balance_due,
                            account_reference=invoice_number,
                            invoice=invoice
                        )
                except Exception as e:
                    print(f"Auto STK push failed: {e}")
        
        return result
    
    def send_payment_reminder(self, invoice):
        """Send payment reminder for overdue invoice"""
        
        customer = None
        if hasattr(invoice, 'customer'):
            customer = invoice.customer
        
        if not customer:
            return {'success': False, 'error': 'Invoice has no customer'}
        
        phone = getattr(customer, 'phone', None)
        if not phone:
            return {'success': False, 'error': 'Customer has no phone number'}
        
        due_date = getattr(invoice, 'due_date', datetime.now().date())
        days_overdue = (datetime.now().date() - due_date).days
        
        customer_name = getattr(customer, 'name', 'Customer')
        invoice_number = getattr(invoice, 'invoice_number', 'N/A')
        balance_due = float(getattr(invoice, 'balance_due', 0))
        invoice_id = getattr(invoice, 'id', '')
        
        variables = {
            'customer_name': customer_name,
            'invoice_number': invoice_number,
            'amount_due': f"KES {balance_due:,.2f}",
            'days_overdue': str(days_overdue),
            'link': f"https://pay.etcash.com/{invoice_id}"
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
        
        invoice = None
        if hasattr(payment, 'invoice'):
            invoice = payment.invoice
        
        if not invoice:
            return {'success': False, 'error': 'Payment has no linked invoice'}
        
        customer = None
        if hasattr(invoice, 'customer'):
            customer = invoice.customer
        
        if not customer:
            return {'success': False, 'error': 'Invoice has no customer'}
        
        phone = getattr(customer, 'phone', None)
        if not phone:
            return {'success': False, 'error': 'Customer has no phone number'}
        
        customer_name = getattr(customer, 'name', 'Customer')
        invoice_number = getattr(invoice, 'invoice_number', 'N/A')
        payment_amount = float(getattr(payment, 'amount', 0))
        balance_due = float(getattr(invoice, 'balance_due', 0))
        payment_date = getattr(payment, 'payment_date', datetime.now().date())
        reference_number = getattr(payment, 'reference_number', '')
        
        variables = {
            'customer_name': customer_name,
            'invoice_number': invoice_number,
            'amount_paid': f"KES {payment_amount:,.2f}",
            'balance': f"KES {balance_due:,.2f}",
            'payment_date': payment_date.strftime('%d/%m/%Y'),
            'mpesa_code': reference_number
        }
        
        return self.send_template_message(
            phone_number=phone,
            template_name='payment_receipt',
            variables=variables,
            invoice=invoice,
            customer=customer
        )
    
    def send_bulk_reminders(self):
        """Send payment reminders to all overdue invoices"""
        
        from datetime import date
        from invoicing.models import Invoice
        
        overdue_invoices = Invoice.objects.filter(
            company=self.company,
            due_date__lt=date.today(),
            status__in=['SENT', 'PARTIAL']
        )
        
        results = []
        for invoice in overdue_invoices:
            if hasattr(invoice, 'customer') and invoice.customer:
                phone = getattr(invoice.customer, 'phone', None)
                if phone:
                    result = self.send_payment_reminder(invoice)
                    results.append({
                        'invoice': getattr(invoice, 'invoice_number', 'N/A'),
                        'success': result.get('success', False)
                    })
        
        return results
    
    def _format_phone(self, phone_number):
        """Format phone number for WhatsApp API"""
        phone = phone_number.strip()
        phone = ''.join(filter(str.isdigit, phone))
        
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            phone = '254' + phone
        
        return phone