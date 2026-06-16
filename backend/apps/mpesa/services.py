from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from .models import MpesaTransaction, MpesaSTKPush, MpesaConfig

class MpesaService:
    """M-Pesa API Integration Service"""
    
    def __init__(self, company):
        self.company = company
        try:
            self.config = MpesaConfig.objects.get(company=company)
        except MpesaConfig.DoesNotExist:
            self.config = None
        
        if self.config and self.config.environment == 'SANDBOX':
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"
    
    def simulate_mpesa_payment(self, phone_number, amount, account_reference, customer_name=""):
        """SIMULATE M-Pesa payment for demo purposes"""
        
        import random
        import string
        
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        receipt_number = ''.join(random.choices(string.digits, k=10))
        
        transaction = MpesaTransaction.objects.create(
            company=self.company,
            transaction_id=transaction_id,
            amount=Decimal(str(amount)),
            currency='KES',
            customer_phone=phone_number,
            customer_name=customer_name or 'Customer',
            business_shortcode=self.config.business_shortcode if self.config else '123456',
            account_reference=account_reference,
            transaction_date=datetime.now(),
            payment_method='MPESA',
            receipt_number=receipt_number,
            status='COMPLETED'
        )
        
        return transaction
    
    def send_stk_push(self, phone_number, amount, account_reference, invoice=None):
        """Send STK Push to customer's phone"""
        
        import random
        import string
        
        phone = phone_number.strip()
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        
        checkout_request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        merchant_request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        
        stk_push = MpesaSTKPush.objects.create(
            company=self.company,
            invoice=invoice,
            phone_number=phone,
            amount=Decimal(str(amount)),
            account_reference=account_reference,
            transaction_description=f"Payment for {account_reference}",
            checkout_request_id=checkout_request_id,
            merchant_request_id=merchant_request_id,
            status='PENDING'
        )
        
        return stk_push
    
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