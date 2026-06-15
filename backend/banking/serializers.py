from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import BankAccount, BankTransaction


class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = [
            'id', 'account', 'transaction_date', 'description', 'reference',
            'amount', 'txn_type', 'reconciled', 'created_at',
        ]


class BankAccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    unreconciled_count = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'currency',
            'opening_balance', 'balance', 'unreconciled_count', 'is_active', 'created_at',
        ]

    def get_balance(self, obj):
        credits = obj.transactions.filter(txn_type='credit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        debits = obj.transactions.filter(txn_type='debit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        return obj.opening_balance + credits - debits

    def get_unreconciled_count(self, obj):
        return obj.transactions.filter(reconciled=False).count()


class BankAccountDetailSerializer(BankAccountSerializer):
    transactions = BankTransactionSerializer(many=True, read_only=True)

    class Meta(BankAccountSerializer.Meta):
        fields = BankAccountSerializer.Meta.fields + ['transactions']
