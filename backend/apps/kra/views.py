from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import KRATaxpayer, KRAPinValidation, KRAVATReturn
from .services import KRAService

class KRAViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        return request.user.profile.company
    
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
        vat_return_id = request.data.get('vat_return_id')
        
        from apps.tax_kenya.models import VATReturn
        
        try:
            vat_return = VATReturn.objects.get(id=vat_return_id, company=company)
            service = KRAService(company)
            result = service.submit_vat_return(vat_return)
            return Response(result)
        except VATReturn.DoesNotExist:
            return Response({'error': 'VAT return not found'}, status=status.HTTP_404_NOT_FOUND)