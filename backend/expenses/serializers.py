from decimal import Decimal

from rest_framework import serializers

from .models import Bill, Expense, Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'email', 'phone', 'kra_pin', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'vendor', 'vendor_name', 'expense_date', 'description', 'category',
            'amount', 'tax_rate', 'tax_amount', 'total_amount', 'payment_method',
            'reference', 'created_at',
        ]

    def validate(self, attrs):
        amount = attrs.get('amount', getattr(self.instance, 'amount', None))
        tax_rate = attrs.get('tax_rate', getattr(self.instance, 'tax_rate', Decimal('0')))
        if amount is not None:
            tax_amount = (amount * tax_rate / Decimal('100')).quantize(Decimal('0.01'))
            attrs['tax_amount'] = tax_amount
            attrs['total_amount'] = amount + tax_amount
        return attrs


class BillSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id', 'vendor', 'vendor_name', 'bill_number', 'issue_date', 'due_date',
            'status', 'subtotal', 'tax_amount', 'total_amount', 'notes', 'created_at',
        ]
