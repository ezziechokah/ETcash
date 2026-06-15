from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

class MobileDashboardViewSet(viewsets.ViewSet):
    """Mobile-optimized endpoints for the mobile app"""
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        return request.user.profile.company
    
    @action(detail=False, methods=['get'])
    def quick_dashboard(self, request):
        """Mobile-friendly quick dashboard with minimal data"""
        company = self.get_company(request)
        
        from apps.sales.models import Invoice
        from apps.banking.models import BankAccount
        
        # Today's stats
        today = timezone.now().date()
        
        today_invoices = Invoice.objects.filter(
            company=company,
            issue_date=today
        )
        
        cash_balance = BankAccount.objects.filter(
            company=company,
            account_type='CASH'
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        bank_balance = BankAccount.objects.filter(
            company=company,
            account_type='BANK'
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        # Overdue invoices count
        overdue_count = Invoice.objects.filter(
            company=company,
            due_date__lt=today,
            status__in=['SENT', 'PARTIAL']
        ).count()
        
        # Quick actions for mobile
        quick_actions = [
            {'id': 'new_invoice', 'title': 'New Invoice', 'icon': 'receipt', 'color': '#2E7D32'},
            {'id': 'record_expense', 'title': 'Add Expense', 'icon': 'money', 'color': '#F57C00'},
            {'id': 'scan_receipt', 'title': 'Scan Receipt', 'icon': 'camera', 'color': '#2196F3'},
            {'id': 'check_stock', 'title': 'Check Stock', 'icon': 'inventory', 'color': '#9C27B0'},
        ]
        
        return Response({
            'cash_position': {
                'cash': float(cash_balance),
                'bank': float(bank_balance),
                'total': float(cash_balance + bank_balance)
            },
            'today': {
                'invoices_count': today_invoices.count(),
                'invoices_total': float(today_invoices.aggregate(total=Sum('total_amount'))['total'] or 0),
                'overdue_count': overdue_count
            },
            'quick_actions': quick_actions,
            'last_sync': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['post'])
    def record_expense_mobile(self, request):
        """Mobile-optimized expense recording with photo capture"""
        company = self.get_company(request)
        
        # Simplified expense creation for mobile
        from apps.purchases.models import Expense
        
        expense = Expense.objects.create(
            company=company,
            category=request.data.get('category'),
            amount=request.data.get('amount'),
            expense_date=request.data.get('expense_date', timezone.now().date()),
            description=request.data.get('description', ''),
            created_by=request.user
        )
        
        # Handle receipt photo if provided
        if request.FILES.get('receipt_photo'):
            expense.receipt = request.FILES['receipt_photo']
            expense.save()
        
        return Response({
            'success': True,
            'expense_id': str(expense.id),
            'message': 'Expense recorded successfully'
        })
    
    @action(detail=False, methods=['get'])
    def offline_data(self, request):
        """Get data for offline mode on mobile"""
        company = self.get_company(request)
        
        from apps.sales.models import Customer, Invoice
        from apps.inventory.models import Product
        
        # Get only essential data for offline use
        customers = Customer.objects.filter(company=company, is_active=True).values('id', 'name', 'phone', 'email')
        products = Product.objects.filter(company=company, is_active=True).values('id', 'sku', 'name', 'sales_price', 'current_quantity')
        
        # Get recent invoices (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_invoices = Invoice.objects.filter(
            company=company,
            issue_date__gte=thirty_days_ago
        ).values('id', 'invoice_number', 'customer_name', 'total_amount', 'status', 'due_date')
        
        return Response({
            'customers': list(customers),
            'products': list(products),
            'recent_invoices': list(recent_invoices),
            'offline_version': '1.0',
            'sync_required': True
        })
    
    @action(detail=False, methods=['post'])
    def sync_offline_data(self, request):
        """Sync offline data from mobile to server"""
        company = self.get_company(request)
        
        offline_data = request.data.get('offline_entries', [])
        
        synced_count = 0
        errors = []
        
        for entry in offline_data:
            try:
                if entry.get('type') == 'invoice':
                    # Create invoice from offline data
                    from apps.sales.models import Invoice, Customer
                    
                    customer, _ = Customer.objects.get_or_create(
                        company=company,
                        name=entry.get('customer_name'),
                        defaults={'phone': entry.get('customer_phone', '')}
                    )
                    
                    Invoice.objects.create(
                        company=company,
                        customer=customer,
                        invoice_number=entry.get('invoice_number'),
                        issue_date=entry.get('issue_date'),
                        due_date=entry.get('due_date'),
                        total_amount=entry.get('total_amount'),
                        created_by=request.user
                    )
                    synced_count += 1
                    
                elif entry.get('type') == 'expense':
                    from apps.purchases.models import Expense
                    Expense.objects.create(
                        company=company,
                        category=entry.get('category'),
                        amount=entry.get('amount'),
                        expense_date=entry.get('expense_date'),
                        description=entry.get('description'),
                        created_by=request.user
                    )
                    synced_count += 1
                    
            except Exception as e:
                errors.append({'entry': entry, 'error': str(e)})
        
        return Response({
            'success': True,
            'synced_count': synced_count,
            'errors': errors
        })