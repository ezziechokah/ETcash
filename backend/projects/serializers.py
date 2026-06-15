from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import Project, ProjectCost


class ProjectCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCost
        fields = ['id', 'project', 'cost_date', 'category', 'description', 'amount', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    total_costs = serializers.SerializerMethodField()
    budget_remaining = serializers.SerializerMethodField()
    costs = ProjectCostSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'client_name', 'status', 'budget',
            'start_date', 'end_date', 'notes', 'total_costs', 'budget_remaining',
            'costs', 'created_at',
        ]

    def get_total_costs(self, obj):
        return obj.costs.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    def get_budget_remaining(self, obj):
        spent = self.get_total_costs(obj)
        return obj.budget - spent


class ProjectListSerializer(serializers.ModelSerializer):
    total_costs = serializers.SerializerMethodField()
    budget_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'client_name', 'status', 'budget',
            'total_costs', 'budget_remaining', 'start_date', 'end_date', 'created_at',
        ]

    def get_total_costs(self, obj):
        return obj.costs.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    def get_budget_remaining(self, obj):
        return obj.budget - self.get_total_costs(obj)
