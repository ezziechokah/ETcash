from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import KRATaxpayer, KRAPinValidation, KRAVATReturn
from .services import KRAService
from django.db import models

class KRAViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        # Try to get company from user profile
        if hasattr(request.user, 'profile') and request.user.profile:
            return request.user.profile.company
        # Fallback: get first company
        from core.models import Company
        return Company.objects.first()
    
    @action(detail=False, methods=['post'])
    def validate_pin(self, request):
        """Validate a KRA PIN"""
        company = self.get_company(request)
        pin = request.data.get('pin')
        
        if not pin:
            return Response({'error': 'PIN is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        service = KRAService(company)
        result = service.validate_pin(pin)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def submit_vat_return(self, request):
        """Submit VAT return to KRA"""
        company = self.get_company(request)
        
        # Get data from request instead of foreign key
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        sales_vat = request.data.get('sales_vat', 0)
        purchases_vat = request.data.get('purchases_vat', 0)
        net_vat = request.data.get('net_vat', 0)
        
        if not period_start or not period_end:
            return Response({'error': 'period_start and period_end are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create KRA VAT return record
        kra_vat_return = KRAVATReturn.objects.create(
            company=company,
            period_start=period_start,
            period_end=period_end,
            sales_vat_declared=sales_vat,
            purchases_vat_declared=purchases_vat,
            net_vat_declared=net_vat,
            status='PENDING'
        )
        
        service = KRAService(company)
        result = service.submit_vat_return(kra_vat_return)
        
        # Update status based on result
        if result.get('success'):
            kra_vat_return.status = 'ACCEPTED'
            kra_vat_return.acknowledgement_receipt = result.get('acknowledgement_receipt', '')
            kra_vat_return.save()
        
        return Response({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'acknowledgement_receipt': kra_vat_return.acknowledgement_receipt,
            'vat_return_id': str(kra_vat_return.id)
        })
    
    @action(detail=False, methods=['get'])
    def vat_returns(self, request):
        """Get list of VAT returns"""
        company = self.get_company(request)
        vat_returns = KRAVATReturn.objects.filter(company=company).order_by('-period_start')
        
        data = []
        for vr in vat_returns:
            data.append({
                'id': str(vr.id),
                'period_start': vr.period_start,
                'period_end': vr.period_end,
                'sales_vat_declared': float(vr.sales_vat_declared),
                'purchases_vat_declared': float(vr.purchases_vat_declared),
                'net_vat_declared': float(vr.net_vat_declared),
                'status': vr.status,
                'submission_date': vr.submission_date,
                'acknowledgement_receipt': vr.acknowledgement_receipt
            })
        
        return Response({
            'count': len(data),
            'results': data
        })
    
    @action(detail=False, methods=['post'])
    def setup_taxpayer(self, request):
        """Setup KRA taxpayer profile"""
        company = self.get_company(request)
        
        pin = request.data.get('pin')
        taxpayer_name = request.data.get('taxpayer_name')
        
        if not pin or not taxpayer_name:
            return Response({'error': 'pin and taxpayer_name are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        taxpayer, created = KRATaxpayer.objects.update_or_create(
            company=company,
            defaults={
                'pin': pin,
                'taxpayer_name': taxpayer_name,
                'is_vat_registered': request.data.get('is_vat_registered', False),
                'is_withholding_tax_agent': request.data.get('is_withholding_tax_agent', False)
            }
        )
        
        return Response({
            'success': True,
            'created': created,
            'taxpayer': {
                'id': str(taxpayer.id),
                'pin': taxpayer.pin,
                'taxpayer_name': taxpayer.taxpayer_name,
                'is_vat_registered': taxpayer.is_vat_registered
            }
        })
    
    @action(detail=False, methods=['get'])
    def taxpayer_profile(self, request):
        """Get KRA taxpayer profile"""
        company = self.get_company(request)
        
        try:
            taxpayer = KRATaxpayer.objects.get(company=company)
            return Response({
                'id': str(taxpayer.id),
                'pin': taxpayer.pin,
                'taxpayer_name': taxpayer.taxpayer_name,
                'is_vat_registered': taxpayer.is_vat_registered,
                'is_withholding_tax_agent': taxpayer.is_withholding_tax_agent,
                'withholding_tax_agent_number': taxpayer.withholding_tax_agent_number,
                'created_at': taxpayer.created_at
            })
        except KRATaxpayer.DoesNotExist:
            return Response({'configured': False}, status=status.HTTP_404_NOT_FOUND)