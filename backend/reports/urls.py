from django.urls import path

from .financial_reports import BalanceSheetView, CashFlowStatementView, ProfitLossView
from .views import CashflowChartView, DashboardStatsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view()),
    path('cashflow-chart/', CashflowChartView.as_view()),
    path('profit-loss/', ProfitLossView.as_view()),
    path('balance-sheet/', BalanceSheetView.as_view()),
    path('cash-flow/', CashFlowStatementView.as_view()),
]
