from decimal import Decimal

from django.db import models

from core.models import Company


class Item(models.Model):
    UNIT_CHOICES = [('each', 'Each'), ('kg', 'Kg'), ('ltr', 'Litre'), ('box', 'Box')]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='items')
    sku = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='each')
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    selling_price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['company', 'sku']]
        ordering = ['name']

    @property
    def stock_value(self):
        return self.quantity_on_hand * self.unit_cost


class StockMovement(models.Model):
    TYPE_CHOICES = [('in', 'Stock In'), ('out', 'Stock Out'), ('adjust', 'Adjustment')]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_movements')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='movements')
    movement_date = models.DateField()
    movement_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date', '-id']

    @property
    def item_name(self):
        return self.item.name
