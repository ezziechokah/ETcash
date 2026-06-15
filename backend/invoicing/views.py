from rest_framework import viewsets

from core.mixins import CompanyScopedMixin

from .models import Customer, Invoice
from .serializers import CustomerSerializer, InvoiceListSerializer, InvoiceSerializer


class CustomerViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class InvoiceViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('customer').prefetch_related('lines')

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = self.get_company()
        return ctx
