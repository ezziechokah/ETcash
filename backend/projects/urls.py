from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectCostViewSet, ProjectViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('costs', ProjectCostViewSet, basename='project-cost')

urlpatterns = [path('', include(router.urls))]
