from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ItemViewSet, StockMovementViewSet

router = DefaultRouter()
router.register('items', ItemViewSet, basename='item')
router.register('movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = [path('', include(router.urls))]
