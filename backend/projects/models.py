from decimal import Decimal

from django.db import models

from core.models import Company


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['company', 'code']]
        ordering = ['-created_at']


class ProjectCost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='project_costs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='costs')
    cost_date = models.DateField()
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cost_date']
