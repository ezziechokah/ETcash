from rest_framework import viewsets

from core.mixins import CompanyScopedMixin

from .models import Bill, Expense, Vendor
from .serializers import BillSerializer, ExpenseSerializer, VendorSerializer


class VendorViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class ExpenseViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('vendor')
    serializer_class = ExpenseSerializer


class BillViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Bill.objects.select_related('vendor')
    serializer_class = BillSerializer
