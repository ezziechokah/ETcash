from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
import json
import hmac
import hashlib
from .models import MpesaTransaction, MpesaConfig

@csrf_exempt
def mpesa_c2b_confirmation(request):
    """Handle C2B transaction confirmation from Safaricom"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Extract transaction details
        transaction_id = data.get('TransID')
        amount = Decimal(data.get('TransAmount', 0))
        phone_number = data.get('MSISDN', '')
        business_shortcode = data.get('BusinessShortCode')
        account_reference = data.get('BillRefNumber', '')
        
        # Find company by business shortcode
        try:
            config = MpesaConfig.objects.get(business_shortcode=business_shortcode)
            company = config.company
        except MpesaConfig.DoesNotExist:
            return JsonResponse({'error': 'Business not found'}, status=404)
        
        # Create transaction record
        transaction, created = MpesaTransaction.objects.get_or_create(
            transaction_id=transaction_id,
            defaults={
                'company': company,
                'amount': amount,
                'customer_phone': phone_number,
                'business_shortcode': business_shortcode,
                'account_reference': account_reference,
                'transaction_date': timezone.now(),
                'status': 'COMPLETED',
                'payment_method': 'MPESA',
            }
        )
        
        # Auto-reconcile with invoice if configured
        if config.auto_reconcile and account_reference:
            try:
                from invoicing.models import Invoice
                invoice = Invoice.objects.get(
                    company=company,
                    invoice_number=account_reference
                )
                transaction.linked_invoice = invoice
                transaction.save()
                
                # Update invoice payment
                invoice.amount_paid += amount
                if invoice.amount_paid >= invoice.total_amount:
                    invoice.status = 'PAID'
                invoice.save()
                
            except Invoice.DoesNotExist:
                pass
        
        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Success"
        })
        
    except Exception as e:
        return JsonResponse({
            "ResultCode": 1,
            "ResultDesc": str(e)
        }, status=500)

@csrf_exempt
def mpesa_stk_callback(request):
    """Handle STK Push callback from Safaricom"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        from .models import MpesaSTKPush
        try:
            stk_push = MpesaSTKPush.objects.get(checkout_request_id=checkout_request_id)
            stk_push.result_code = result_code
            stk_push.result_desc = result_desc
            
            if result_code == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                items = {item['Name']: item['Value'] for item in callback_metadata.get('Item', [])}
                
                stk_push.status = 'SUCCESS'
                stk_push.mpesa_receipt_number = items.get('MpesaReceiptNumber', '')
                stk_push.transaction_date = timezone.now()
                stk_push.completed_at = timezone.now()
                stk_push.save()
                
                # Create transaction record
                MpesaTransaction.objects.create(
                    company=stk_push.company,
                    transaction_id=items.get('MpesaReceiptNumber', ''),
                    amount=stk_push.amount,
                    customer_phone=stk_push.phone_number,
                    business_shortcode=stk_push.company.mpesa_config.business_shortcode if hasattr(stk_push.company, 'mpesa_config') else '',
                    account_reference=stk_push.account_reference,
                    transaction_date=timezone.now(),
                    status='COMPLETED',
                    checkout_request_id=checkout_request_id,
                    merchant_request_id=stk_push.merchant_request_id
                )
            else:
                stk_push.status = 'FAILED'
                stk_push.completed_at = timezone.now()
                stk_push.save()
                
        except MpesaSTKPush.DoesNotExist:
            pass
        
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
        
    except Exception as e:
        return JsonResponse({"ResultCode": 1, "ResultDesc": str(e)}, status=500)