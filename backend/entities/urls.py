from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConsolidationView, LegalEntityViewSet

router = DefaultRouter()
router.register('list', LegalEntityViewSet, basename='legal-entity')

urlpatterns = [
    path('', include(router.urls)),
    path('consolidation/', ConsolidationView.as_view()),
]
