from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from .models import MpesaConfig, MpesaTransaction, MpesaSTKPush
from .serializers import (
    MpesaConfigSerializer, MpesaTransactionSerializer, 
    MpesaSTKPushSerializer, STKPushRequestSerializer,
    MpesaReconcileSerializer
)

class MpesaViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        # Get company from user profile
        if hasattr(request.user, 'profile') and request.user.profile:
            return request.user.profile.company
        # Fallback: get first company
        from core.models import Company
        return Company.objects.first()
    
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
        
        # Generate sample transaction ID
        transaction_id = f"MPESA{random.randint(100000000, 999999999)}"
        receipt_number = f"QK{random.randint(10000000, 99999999)}"
        
        # Create transaction
        transaction = MpesaTransaction.objects.create(
            company=company,
            transaction_id=transaction_id,
            amount=Decimal(str(amount)),
            customer_phone=phone,
            customer_name=request.data.get('customer_name', 'Customer'),
            business_shortcode="123456",
            account_reference=account_ref,
            transaction_date=timezone.now(),
            receipt_number=receipt_number,
            status='COMPLETED'
        )
        
        return Response({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'amount': float(transaction.amount),
            'receipt_number': receipt_number,
            'message': f"Payment of KES {amount} from {phone} to {account_ref} simulated successfully"
        })
    
    @action(detail=False, methods=['post'])
    def send_stk_push(self, request):
        """Send STK Push to customer"""
        company = self.get_company(request)
        serializer = STKPushRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            checkout_id = f"CHECKOUT{random.randint(100000000, 999999999)}"
            merchant_id = f"MERCHANT{random.randint(100000000, 999999999)}"
            
            stk_push = MpesaSTKPush.objects.create(
                company=company,
                phone_number=serializer.validated_data['phone_number'],
                amount=serializer.validated_data['amount'],
                account_reference=serializer.validated_data['account_reference'],
                transaction_description=f"Payment for {serializer.validated_data['account_reference']}",
                checkout_request_id=checkout_id,
                merchant_request_id=merchant_id,
                status='PENDING'
            )
            
            return Response({
                'success': True,
                'checkout_request_id': stk_push.checkout_request_id,
                'status': stk_push.status,
                'message': f"STK Push sent to {serializer.validated_data['phone_number']}. Please check your phone for M-Pesa prompt."
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get M-Pesa transactions"""
        company = self.get_company(request)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        
        queryset = MpesaTransaction.objects.filter(company=company)
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        queryset = queryset.order_by('-transaction_date')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = MpesaTransactionSerializer(queryset[start:end], many=True)
        
        return Response({
            'count': queryset.count(),
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
        for i in range(min(days, 30)):
            date = (timezone.now() - timedelta(days=i)).date()
            day_transactions = transactions.filter(transaction_date__date=date)
            daily_data.append({
                'date': date.isoformat(),
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
                
                transaction.status = 'RECONCILED'
                transaction.save()
                
                return Response({
                    'success': True,
                    'message': f"Transaction {transaction.transaction_id} reconciled successfully"
                })
                
            except MpesaTransaction.DoesNotExist:
                return Response({
                    'success': False,
                    'message': "Transaction not found"
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Public test views
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def public_stats(request):
    """Public endpoint for testing - no auth required"""
    config = MpesaConfig.objects.first()
    transactions = MpesaTransaction.objects.all()
    
    return JsonResponse({
        'mpesa_configured': config is not None,
        'business_name': config.business_name if config else None,
        'paybill': config.business_shortcode if config else None,
        'total_transactions': transactions.count(),
        'total_amount': float(transactions.aggregate(total=Sum('amount'))['total'] or 0),
        'sample_transactions': [
            {
                'id': str(t.id),
                'amount': float(t.amount),
                'customer': t.customer_name,
                'phone': t.customer_phone,
                'date': t.transaction_date.strftime('%Y-%m-%d')
            }
            for t in transactions[:5]
        ]
    })

@csrf_exempt
def test_view(request):
    """Simple test endpoint"""
    config = MpesaConfig.objects.first()
    return JsonResponse({
        'status': 'ok',
        'message': 'M-Pesa app is working!',
        'mpesa_configured': config is not None,
        'business_name': config.business_name if config else None,
        'paybill': config.business_shortcode if config else None,
    })
