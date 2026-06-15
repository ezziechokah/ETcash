from rest_framework import viewsets

from core.mixins import CompanyScopedMixin

from .models import Item, StockMovement
from .serializers import ItemSerializer, StockMovementSerializer


class ItemViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class StockMovementViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related('item')
    serializer_class = StockMovementSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())
