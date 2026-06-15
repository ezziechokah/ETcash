from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import CompanyScopedMixin

from .models import BankAccount, BankTransaction
from .serializers import BankAccountDetailSerializer, BankAccountSerializer, BankTransactionSerializer


class BankAccountViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = BankAccount.objects.prefetch_related('transactions')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BankAccountDetailSerializer
        return BankAccountSerializer


class BankTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = BankTransactionSerializer

    def get_company(self):
        return self.request.user.profile.company

    def get_queryset(self):
        return BankTransaction.objects.filter(account__company=self.get_company())

    @action(detail=True, methods=['post'])
    def reconcile(self, request, pk=None):
        txn = self.get_object()
        txn.reconciled = request.data.get('reconciled', True)
        txn.save(update_fields=['reconciled'])
        return Response(BankTransactionSerializer(txn).data)
