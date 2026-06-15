from django.db import models
from uuid import uuid4

class MobileSyncLog(models.Model):
    """Track mobile sync operations"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=50, choices=[
        ('FULL', 'Full Sync'),
        ('INCREMENTAL', 'Incremental Sync'),
        ('OFFLINE_UPLOAD', 'Offline Upload'),
    ])
    records_synced = models.IntegerField(default=0)
    sync_date = models.DateTimeField(auto_now_add=True)
    sync_duration_seconds = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='SUCCESS')
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Sync by {self.user.username} at {self.sync_date}"