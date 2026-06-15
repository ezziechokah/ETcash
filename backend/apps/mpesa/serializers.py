from rest_framework import serializers
from .models import MpesaConfig, MpesaTransaction, MpesaSTKPush

class MpesaConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaConfig
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class MpesaTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class MpesaSTKPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaSTKPush
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class STKPushRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    account_reference = serializers.CharField(max_length=50)
    invoice_id = serializers.UUIDField(required=False, allow_null=True)

class MpesaReconcileSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=50)