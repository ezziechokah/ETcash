from django.contrib import admin

from .models import Bill, Expense, Vendor

admin.site.register(Vendor)
admin.site.register(Expense)
admin.site.register(Bill)
