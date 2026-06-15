from django.db import models

from core.models import Company


class LegalEntity(models.Model):
    """Subsidiary or branch under a multi-entity group."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='legal_entities')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    kra_pin = models.CharField(max_length=20, blank=True)
    currency = models.CharField(max_length=3, default='KES')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['company', 'code']]
        ordering = ['name']
