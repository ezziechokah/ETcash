from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import WhatsAppConfig, WhatsAppMessage, WhatsAppTemplate
from .services import WhatsAppService

class WhatsAppViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_company(self, request):
        return request.user.profile.company
    
    @action(detail=False, methods=['post'])
    def send_invoice(self, request):
        """Send invoice via WhatsApp"""
        company = self.get_company(request)
        invoice_id = request.data.get('invoice_id')
        
        from apps.sales.models import Invoice
        
        try:
            invoice = Invoice.objects.get(id=invoice_id, company=company)
            service = WhatsAppService(company)
            result = service.send_invoice(invoice)
            return Response(result)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def send_reminder(self, request):
        """Send payment reminder via WhatsApp"""
        company = self.get_company(request)
        invoice_id = request.data.get('invoice_id')
        
        from apps.sales.models import Invoice
        
        try:
            invoice = Invoice.objects.get(id=invoice_id, company=company)
            service = WhatsAppService(company)
            result = service.send_payment_reminder(invoice)
            return Response(result)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def send_bulk_reminders(self, request):
        """Send bulk payment reminders"""
        company = self.get_company(request)
        service = WhatsAppService(company)
        results = service.send_bulk_reminders()
        return Response({'results': results})