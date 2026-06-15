from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KRAViewSet

router = DefaultRouter()
router.register(r'kra', KRAViewSet, basename='kra')

urlpatterns = [
    path('', include(router.urls)),
]