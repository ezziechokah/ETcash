from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .webhooks import mpesa_c2b_confirmation, mpesa_stk_callback

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.MpesaViewSet, basename='mpesa')

# Define urlpatterns
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Test endpoints
    path('test/', views.test_view, name='test'),
    path('public-stats/', views.public_stats, name='public_stats'),
    
    # Direct action endpoints
    path('config/', views.MpesaViewSet.as_view({'get': 'config'}), name='config'),
    path('simulate_payment/', views.MpesaViewSet.as_view({'post': 'simulate_payment'}), name='simulate_payment'),
    path('send_stk_push/', views.MpesaViewSet.as_view({'post': 'send_stk_push'}), name='send_stk_push'),
    path('transactions/', views.MpesaViewSet.as_view({'get': 'transactions'}), name='transactions'),
    path('dashboard_stats/', views.MpesaViewSet.as_view({'get': 'dashboard_stats'}), name='dashboard_stats'),
    path('reconcile/', views.MpesaViewSet.as_view({'post': 'reconcile'}), name='reconcile'),
    
    # Webhook endpoints (no authentication required)
    path('webhook/c2b/', mpesa_c2b_confirmation, name='c2b_webhook'),
    path('webhook/stk/', mpesa_stk_callback, name='stk_webhook'),
]