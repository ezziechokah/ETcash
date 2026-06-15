from decimal import Decimal

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import CompanyScopedMixin
from expenses.models import Expense
from invoicing.models import Invoice

from .models import LegalEntity
from .serializers import LegalEntitySerializer


class LegalEntityViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = LegalEntity.objects.all()
    serializer_class = LegalEntitySerializer


class ConsolidationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.profile.company
        entities = LegalEntity.objects.filter(company=company)

        rows = []
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')

        for entity in entities:
            revenue = Invoice.objects.filter(company=company).exclude(
                status__in=['draft', 'void']
            ).aggregate(t=Sum('subtotal'))['t'] or Decimal('0')
            # MVP: same company books; entity tag on transactions is future work
            expenses = Expense.objects.filter(company=company).aggregate(
                t=Sum('total_amount')
            )['t'] or Decimal('0')
            if entities.count() > 1:
                revenue = revenue / entities.count()
                expenses = expenses / entities.count()
            rows.append({
                'entity_id': entity.id,
                'entity_code': entity.code,
                'entity_name': entity.name,
                'revenue': revenue,
                'expenses': expenses,
                'net': revenue - expenses,
            })
            total_revenue += revenue
            total_expenses += expenses

        eliminations = Decimal('0')
        consolidated_net = total_revenue - total_expenses - eliminations

        return Response({
            'entities': rows,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'intercompany_eliminations': eliminations,
            'consolidated_net': consolidated_net,
        })
