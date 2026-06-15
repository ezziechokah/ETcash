from django.urls import path

from .tax_reports import VatReportView, WhtReportView
from .views import TaxInsightsView

urlpatterns = [
    path('insights/', TaxInsightsView.as_view()),
    path('vat-report/', VatReportView.as_view()),
    path('wht-report/', WhtReportView.as_view()),
]
