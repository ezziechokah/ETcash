from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BillViewSet, ExpenseViewSet, VendorViewSet

router = DefaultRouter()
router.register('vendors', VendorViewSet, basename='vendor')
router.register('expenses', ExpenseViewSet, basename='expense')
router.register('bills', BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
]
