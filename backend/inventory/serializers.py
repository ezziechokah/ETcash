from decimal import Decimal

from rest_framework import serializers

from .models import Item, StockMovement


class ItemSerializer(serializers.ModelSerializer):
    stock_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'sku', 'name', 'unit', 'quantity_on_hand', 'unit_cost',
            'selling_price', 'reorder_level', 'stock_value', 'is_active', 'created_at',
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(read_only=True)
    sku = serializers.CharField(source='item.sku', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'sku', 'movement_date', 'movement_type',
            'quantity', 'reference', 'notes', 'created_at',
        ]

    def create(self, validated_data):
        movement = StockMovement.objects.create(**validated_data)
        item = movement.item
        qty = movement.quantity
        if movement.movement_type == 'in':
            item.quantity_on_hand += qty
        elif movement.movement_type == 'out':
            item.quantity_on_hand = max(Decimal('0'), item.quantity_on_hand - qty)
        else:
            item.quantity_on_hand = qty
        item.save(update_fields=['quantity_on_hand'])
        return movement
