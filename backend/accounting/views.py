from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import CompanyScopedMixin

from .models import Account, JournalEntry
from .serializers import AccountSerializer, JournalEntryListSerializer, JournalEntrySerializer


class AccountViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        company = self.get_company()
        from .seed import seed_chart_of_accounts
        if not Account.objects.filter(company=company).exists():
            seed_chart_of_accounts(company)
        return super().list(request, *args, **kwargs)


class JournalEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = JournalEntry.objects.prefetch_related('lines', 'lines__account')

    def get_serializer_class(self):
        if self.action == 'list':
            return JournalEntryListSerializer
        return JournalEntrySerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['company'] = self.get_company()
        return ctx

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())

    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        entry = self.get_object()
        if entry.status == 'posted':
            return Response({'detail': 'Already posted.'}, status=status.HTTP_400_BAD_REQUEST)
        debit = sum(l.debit for l in entry.lines.all())
        credit = sum(l.credit for l in entry.lines.all())
        if debit != credit:
            return Response({'detail': 'Entry is not balanced.'}, status=status.HTTP_400_BAD_REQUEST)
        entry.status = 'posted'
        entry.save(update_fields=['status'])
        return Response(JournalEntrySerializer(entry).data)
