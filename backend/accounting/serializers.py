from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import Account, JournalEntry, JournalLine


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'code', 'name', 'account_type', 'is_active', 'description', 'balance']

    def get_balance(self, obj):
        agg = JournalLine.objects.filter(
            account=obj,
            entry__company=obj.company,
            entry__status='posted',
        ).aggregate(debit=Sum('debit'), credit=Sum('credit'))
        debit = agg['debit'] or Decimal('0')
        credit = agg['credit'] or Decimal('0')
        if obj.account_type in ('asset', 'expense'):
            return debit - credit
        return credit - debit


class JournalLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = JournalLine
        fields = ['id', 'account', 'account_code', 'account_name', 'description', 'debit', 'credit']


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True)
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_date', 'reference', 'description', 'status',
            'lines', 'total_debit', 'total_credit', 'created_at',
        ]

    def get_total_debit(self, obj):
        return sum((l.debit for l in obj.lines.all()), Decimal('0'))

    def get_total_credit(self, obj):
        return sum((l.credit for l in obj.lines.all()), Decimal('0'))

    def validate_lines(self, lines):
        if len(lines) < 2:
            raise serializers.ValidationError('At least two lines are required.')
        return lines

    def validate(self, attrs):
        if 'lines' not in attrs and self.instance:
            return attrs
        lines = attrs.get('lines', [])
        debit = sum(l.get('debit', Decimal('0')) for l in lines)
        credit = sum(l.get('credit', Decimal('0')) for l in lines)
        if debit != credit:
            raise serializers.ValidationError('Debits must equal credits.')
        return attrs

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        company = self.context['company']
        entry = JournalEntry.objects.create(company=company, **validated_data)
        self._save_lines(entry, lines_data, company)
        return entry

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if lines_data is not None:
            instance.lines.all().delete()
            self._save_lines(instance, lines_data, instance.company)
        return instance

    def _save_lines(self, entry, lines_data, company):
        for line in lines_data:
            account = line['account']
            if account.company_id != company.id:
                raise serializers.ValidationError('Invalid account for this company.')
            JournalLine.objects.create(entry=entry, **line)


class JournalEntryListSerializer(serializers.ModelSerializer):
    total_debit = serializers.SerializerMethodField()
    line_count = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = ['id', 'entry_date', 'reference', 'description', 'status', 'total_debit', 'line_count', 'created_at']

    def get_total_debit(self, obj):
        return sum((l.debit for l in obj.lines.all()), Decimal('0'))

    def get_line_count(self, obj):
        return obj.lines.count()
