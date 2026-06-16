from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.kra_test, name='kra_test'),
    path('validate_pin/', views.validate_pin, name='validate_pin'),
    path('setup_taxpayer/', views.setup_taxpayer, name='setup_taxpayer'),
    path('taxpayer_profile/', views.taxpayer_profile, name='taxpayer_profile'),
    path('submit_vat_return/', views.submit_vat_return, name='submit_vat_return'),
    path('vat_returns/', views.vat_returns, name='vat_returns'),
]
