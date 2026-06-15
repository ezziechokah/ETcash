from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MobileDashboardViewSet

router = DefaultRouter()
router.register(r'mobile', MobileDashboardViewSet, basename='mobile')

urlpatterns = [
    path('', include(router.urls)),
]