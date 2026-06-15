import requests
import json
import base64
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from .models import MpesaTransaction, MpesaSTKPush, MpesaConfig

class MpesaService:
    """M-Pesa API Integration Service"""
    
    def __init__(self, company):
        self.company = company
        self.config = MpesaConfig.objects.get(company=company)
        
        # Set API endpoints
        if self.config.environment == 'SANDBOX':
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"
    
    def get_access_token(self):
        """Get OAuth access token from M-Pesa"""
        cache_key = f"mpesa_token_{self.config.id}"
        token = cache.get(cache_key)
        
        if token:
            return token
        
        # For demo/sample purposes, return a sample token
        if settings.DEBUG:
            return "sample_access_token_demo_" + datetime.now().strftime("%Y%m%d")
        
        # In production, actual API call:
        """
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.config.consumer_key}:{self.config.consumer_secret}".encode()).decode()
        
        headers = {"Authorization": f"Basic {auth}"}
        response = requests.get(auth_url, headers=headers)
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            cache.set(cache_key, token, 3540)  # Cache for 59 minutes
            return token
        """
        
        return None
    
    def simulate_mpesa_payment(self, phone_number, amount, account_reference):
        """SIMULATE M-Pesa payment for demo purposes"""
        
        # Generate sample transaction ID
        import random
        import string
        
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        receipt_number = ''.join(random.choices(string.digits, k=10))
        
        # Create transaction record
        transaction = MpesaTransaction.objects.create(
            company=self.company,
            transaction_id=transaction_id,
            amount=amount,
            currency='KES',
            customer_phone=phone_number,
            business_shortcode=self.config.business_shortcode,
            account_reference=account_reference,
            transaction_date=datetime.now(),
            payment_method='MPESA',
            receipt_number=receipt_number,
            status='COMPLETED'
        )
        
        # Auto-reconcile if enabled
        if self.config.auto_reconcile:
            self.reconcile_payment(transaction)
        
        return transaction
    
    def send_stk_push(self, phone_number, amount, account_reference, invoice=None):
        """Send STK Push to customer's phone"""
        
        # Format phone number (remove 0 or +254, add 254)
        phone = phone_number.strip()
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        
        # Generate unique IDs
        import random
        import string
        
        checkout_request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        merchant_request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        
        # Create STK push record
        stk_push = MpesaSTKPush.objects.create(
            company=self.company,
            invoice=invoice,
            phone_number=phone,
            amount=amount,
            account_reference=account_reference,
            transaction_description=f"Payment for {account_reference}",
            checkout_request_id=checkout_request_id,
            merchant_request_id=merchant_request_id,
            status='PENDING'
        )
        
        # For demo, simulate success after 2 seconds
        # In production, this would be an actual API call
        
        return stk_push
    
    def reconcile_payment(self, mpesa_transaction):
        """Automatically reconcile M-Pesa payment with invoice"""
        from apps.sales.models import Invoice, Payment
        from decimal import Decimal
        
        # Find invoice by account reference (invoice number)
        if mpesa_transaction.account_reference:
            try:
                invoice = Invoice.objects.get(
                    company=self.company,
                    invoice_number=mpesa_transaction.account_reference
                )
                
                # Create payment record
                payment = Payment.objects.create(
                    company=self.company,
                    invoice=invoice,
                    payment_date=mpesa_transaction.transaction_date.date(),
                    amount=mpesa_transaction.amount,
                    payment_method='MPESA',
                    reference_number=mpesa_transaction.transaction_id,
                    notes=f"M-Pesa payment - {mpesa_transaction.transaction_id}"
                )
                
                # Link transaction to payment
                mpesa_transaction.linked_invoice = invoice
                mpesa_transaction.linked_payment = payment
                mpesa_transaction.save()
                
                return payment
                
            except Invoice.DoesNotExist:
                pass
        
        return None
    
    def get_transactions(self, start_date=None, end_date=None, status=None):
        """Get M-Pesa transactions with filters"""
        queryset = MpesaTransaction.objects.filter(company=self.company)
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset

class MpesaWebhookHandler:
    """Handle M-Pesa webhook callbacks"""
    
    @staticmethod
    def handle_c2b_confirmation(data, company):
        """Handle C2B transaction confirmation webhook"""
        from apps.sales.models import Invoice
        
        transaction = MpesaTransaction.objects.create(
            company=company,
            transaction_id=data.get('TransID'),
            amount=Decimal(data.get('TransAmount', 0)),
            currency='KES',
            customer_phone=data.get('MSISDN', ''),
            customer_name=data.get('FirstName', '') + ' ' + data.get('MiddleName', '') + ' ' + data.get('LastName', ''),
            business_shortcode=data.get('BusinessShortCode'),
            account_reference=data.get('BillRefNumber', ''),
            transaction_date=datetime.strptime(data.get('TransTime'), '%Y%m%d%H%M%S'),
            payment_method='MPESA',
            receipt_number=data.get('TransID'),
            status='COMPLETED',
            raw_callback_data=data
        )
        
        # Auto-reconcile
        service = MpesaService(company)
        service.reconcile_payment(transaction)
        
        return transaction
    
    @staticmethod
    def handle_stk_push_callback(data, company):
        """Handle STK Push callback from M-Pesa"""
        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        try:
            stk_push = MpesaSTKPush.objects.get(checkout_request_id=checkout_request_id, company=company)
            stk_push.result_code = result_code
            stk_push.result_desc = result_desc
            
            if result_code == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                items = {item['Name']: item['Value'] for item in callback_metadata.get('Item', [])}
                
                stk_push.status = 'SUCCESS'
                stk_push.mpesa_receipt_number = items.get('MpesaReceiptNumber', '')
                stk_push.transaction_date = datetime.now()
                stk_push.customer_phone = items.get('PhoneNumber', '')
                stk_push.customer_name = items.get('CustomerName', '')
                stk_push.completed_at = datetime.now()
                stk_push.save()
                
                # Create transaction record
                transaction = MpesaTransaction.objects.create(
                    company=company,
                    transaction_id=items.get('MpesaReceiptNumber', ''),
                    amount=Decimal(items.get('Amount', 0)),
                    currency='KES',
                    customer_phone=items.get('PhoneNumber', ''),
                    customer_name=items.get('CustomerName', ''),
                    business_shortcode=stk_push.invoice.company.mpesa_config.business_shortcode if stk_push.invoice else '',
                    account_reference=stk_push.account_reference,
                    transaction_date=datetime.now(),
                    status='COMPLETED',
                    checkout_request_id=checkout_request_id,
                    merchant_request_id=stk_push.merchant_request_id
                )
                
                # Link to invoice if exists
                if stk_push.invoice:
                    transaction.linked_invoice = stk_push.invoice
                    transaction.save()
                    
                    # Auto-reconcile
                    service = MpesaService(company)
                    service.reconcile_payment(transaction)
                
            else:
                stk_push.status = 'FAILED'
                stk_push.completed_at = datetime.now()
                stk_push.save()
                
        except MpesaSTKPush.DoesNotExist:
            pass
        
        return {"ResultCode": 0, "ResultDesc": "Success"}