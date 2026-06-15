from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import MpesaConfig, MpesaTransaction, MpesaSTKPush
from .services import MpesaService, MpesaWebhookHandler
from .serializers import (
    MpesaConfigSerializer, MpesaTransactionSerializer, 
    MpesaSTKPushSerializer, STKPushRequestSerializer,
    MpesaReconcileSerializer
)

class MpesaViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        return request.user.profile.company
    
    @action(detail=False, methods=['get'])
    def config(self, request):
        """Get M-Pesa configuration"""
        company = self.get_company(request)
        try:
            config = MpesaConfig.objects.get(company=company)
            serializer = MpesaConfigSerializer(config)
            return Response(serializer.data)
        except MpesaConfig.DoesNotExist:
            return Response({'configured': False}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def setup_config(self, request):
        """Setup M-Pesa configuration"""
        company = self.get_company(request)
        serializer = MpesaConfigSerializer(data=request.data)
        
        if serializer.is_valid():
            config, created = MpesaConfig.objects.update_or_create(
                company=company,
                defaults=serializer.validated_data
            )
            return Response(MpesaConfigSerializer(config).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def simulate_payment(self, request):
        """Simulate M-Pesa payment for demo/testing"""
        company = self.get_company(request)
        phone = request.data.get('phone_number')
        amount = request.data.get('amount')
        account_ref = request.data.get('account_reference')
        
        if not all([phone, amount, account_ref]):
            return Response(
                {'error': 'phone_number, amount, and account_reference are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = MpesaService(company)
        transaction = service.simulate_mpesa_payment(phone, amount, account_ref)
        
        return Response({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'amount': float(transaction.amount),
            'message': f"Payment of KES {amount} from {phone} to {account_ref} simulated successfully"
        })
    
    @action(detail=False, methods=['post'])
    def send_stk_push(self, request):
        """Send STK Push to customer"""
        company = self.get_company(request)
        serializer = STKPushRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = MpesaService(company)
            stk_push = service.send_stk_push(
                phone_number=serializer.validated_data['phone_number'],
                amount=serializer.validated_data['amount'],
                account_reference=serializer.validated_data['account_reference'],
                invoice=serializer.validated_data.get('invoice_id')
            )
            
            return Response({
                'success': True,
                'checkout_request_id': stk_push.checkout_request_id,
                'status': stk_push.status,
                'message': f"STK Push sent to {serializer.validated_data['phone_number']}"
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get M-Pesa transactions"""
        company = self.get_company(request)
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        service = MpesaService(company)
        transactions = service.get_transactions(start_date, end_date, status_filter)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = MpesaTransactionSerializer(transactions[start:end], many=True)
        
        return Response({
            'count': transactions.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get M-Pesa dashboard statistics"""
        company = self.get_company(request)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        transactions = MpesaTransaction.objects.filter(
            company=company,
            transaction_date__gte=start_date,
            status='COMPLETED'
        )
        
        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
        # Daily breakdown
        daily_data = []
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_transactions = transactions.filter(transaction_date__date=date)
            daily_data.append({
                'date': date,
                'count': day_transactions.count(),
                'total': float(day_transactions.aggregate(total=Sum('amount'))['total'] or 0)
            })
        
        return Response({
            'period_days': days,
            'total_transactions': transactions.count(),
            'total_amount': float(total_amount),
            'average_transaction': float(total_amount / transactions.count()) if transactions.count() > 0 else 0,
            'daily_breakdown': daily_data,
            'recent_transactions': MpesaTransactionSerializer(transactions[:10], many=True).data
        })
    
    @action(detail=False, methods=['post'])
    def reconcile(self, request):
        """Manually reconcile M-Pesa transaction with invoice"""
        company = self.get_company(request)
        serializer = MpesaReconcileSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                transaction = MpesaTransaction.objects.get(
                    company=company,
                    transaction_id=serializer.validated_data['transaction_id']
                )
                
                service = MpesaService(company)
                payment = service.reconcile_payment(transaction)
                
                if payment:
                    return Response({
                        'success': True,
                        'message': f"Transaction reconciled with invoice {payment.invoice.invoice_number}",
                        'payment_id': str(payment.id)
                    })
                else:
                    return Response({
                        'success': False,
                        'message': "Could not find matching invoice for this transaction"
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except MpesaTransaction.DoesNotExist:
                return Response({
                    'success': False,
                    'message': "Transaction not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def webhook_c2b_confirmation(self, request):
        """Webhook endpoint for C2B confirmations"""
        # In production, identify company from the request
        # For demo, we'll accept and log
        company = self.get_company(request)  # This needs authentication in production
        
        handler = MpesaWebhookHandler()
        transaction = handler.handle_c2b_confirmation(request.data, company)
        
        return Response({
            "ResultCode": 0,
            "ResultDesc": "Success"
        })
    
    @action(detail=False, methods=['post'])
    def webhook_stk_callback(self, request):
        """Webhook endpoint for STK Push callbacks"""
        company = self.get_company(request)
        
        handler = MpesaWebhookHandler()
        result = handler.handle_stk_push_callback(request.data, company)
        
        return Response(result)