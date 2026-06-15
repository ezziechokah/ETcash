from django.conf import settings
from django.db import models


class Company(models.Model):
    MODE_CHOICES = [
        ('freelancer', 'Freelancer'),
        ('sme', 'SME'),
        ('multi_entity', 'Multi-Entity'),
    ]

    name = models.CharField(max_length=200)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='sme')
    kra_pin = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    fy_start_month = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    full_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user.username
