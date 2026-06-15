from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/invoicing/', include('invoicing.urls')),
    path('api/accounting/', include('accounting.urls')),
    path('api/expenses/', include('expenses.urls')),
    path('api/banking/', include('banking.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/entities/', include('entities.urls')),
    path('api/payroll/', include('payroll.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/tax/', include('reports.tax_urls')),
]
