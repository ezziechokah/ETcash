from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Company
from invoicing.models import Customer, Invoice
from mpesa.models import MpesaTransaction

from sample_servers import catalog


class SampleInfoView(APIView):
    """Return sample data catalog — useful while real integrations are pending."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'mode': 'sample',
            'description': 'Demo data served locally until real company and integration credentials are provided.',
            'login': {
                'username': catalog.SAMPLE_ADMIN['username'],
                'note': 'Password is set during seed (default: Admin1234!)',
            },
            'company': catalog.SAMPLE_COMPANY,
            'customers_count': len(catalog.SAMPLE_CUSTOMERS),
            'vendors_count': len(catalog.SAMPLE_VENDORS),
            'integrations': {
                'mpesa': {'environment': catalog.SAMPLE_MPESA['environment'], 'shortcode': catalog.SAMPLE_MPESA['business_shortcode']},
                'kra': {'valid_pins': catalog.VALID_KRA_PINS, 'sample_pin': catalog.SAMPLE_KRA['pin']},
            },
        })


class SampleStatusView(APIView):
    """Report whether sample data has been loaded into the database."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = getattr(getattr(request.user, 'profile', None), 'company', None)
        if not company:
            company = Company.objects.first()

        if not company:
            return Response({'loaded': False, 'message': 'No company configured. Run: python manage.py seed_sample'})

        return Response({
            'loaded': True,
            'company': company.name,
            'mode': company.mode,
            'counts': {
                'customers': Customer.objects.filter(company=company).count(),
                'invoices': Invoice.objects.filter(company=company).count(),
                'mpesa_transactions': MpesaTransaction.objects.filter(company=company).count(),
            },
            'sample_login': catalog.SAMPLE_ADMIN['username'],
        })
