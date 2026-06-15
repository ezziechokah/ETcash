from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, PayrollRunViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register('runs', PayrollRunViewSet, basename='payroll-run')

urlpatterns = [path('', include(router.urls))]
