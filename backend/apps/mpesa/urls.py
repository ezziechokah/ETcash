from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MpesaViewSet

router = DefaultRouter()
router.register(r'mpesa', MpesaViewSet, basename='mpesa')

urlpatterns = [
    path('', include(router.urls)),
]