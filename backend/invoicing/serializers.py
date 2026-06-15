from decimal import Decimal

from rest_framework import serializers

from .models import Customer, Invoice, InvoiceLine
from .utils import compute_line_totals, next_invoice_number


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'kra_pin', 'created_at']


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ['id', 'description', 'quantity', 'unit_price', 'tax_rate', 'line_total']
        read_only_fields = ['line_total']


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(read_only=True)
    lines = InvoiceLineSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_name',
            'issue_date', 'due_date', 'status', 'subtotal', 'tax_amount',
            'total_amount', 'notes', 'lines', 'created_at',
        ]
        read_only_fields = ['invoice_number', 'subtotal', 'tax_amount', 'total_amount']

    def _totals_from_lines(self, lines_data):
        subtotal = Decimal('0')
        tax_amount = Decimal('0')
        for line in lines_data:
            qty = Decimal(str(line.get('quantity', 1)))
            price = Decimal(str(line['unit_price']))
            rate = Decimal(str(line.get('tax_rate', 16)))
            _, sub, tax = compute_line_totals(qty, price, rate)
            subtotal += sub
            tax_amount += tax
        return subtotal, tax_amount, subtotal + tax_amount

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        company = self.context['company']
        subtotal, tax_amount, total = self._totals_from_lines(lines_data)
        invoice = Invoice.objects.create(
            company=company,
            invoice_number=next_invoice_number(company),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total,
            **validated_data,
        )
        self._create_lines(invoice, lines_data)
        return invoice

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if lines_data is not None:
            instance.lines.all().delete()
            self._create_lines(instance, lines_data)
            subtotal, tax_amount, total = self._totals_from_lines(lines_data)
            instance.subtotal = subtotal
            instance.tax_amount = tax_amount
            instance.total_amount = total
        instance.save()
        return instance

    def _create_lines(self, invoice, lines_data):
        for line in lines_data:
            qty = Decimal(str(line.get('quantity', 1)))
            price = Decimal(str(line['unit_price']))
            rate = Decimal(str(line.get('tax_rate', 16)))
            line_total, _, _ = compute_line_totals(qty, price, rate)
            InvoiceLine.objects.create(
                invoice=invoice,
                description=line['description'],
                quantity=qty,
                unit_price=price,
                tax_rate=rate,
                line_total=line_total,
            )


class InvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_name',
            'issue_date', 'due_date', 'status', 'total_amount', 'created_at',
        ]
