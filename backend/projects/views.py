from rest_framework import viewsets

from core.mixins import CompanyScopedMixin

from .models import Project, ProjectCost
from .serializers import ProjectCostSerializer, ProjectListSerializer, ProjectSerializer


class ProjectViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related('costs')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectCostViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset = ProjectCost.objects.select_related('project')
    serializer_class = ProjectCostSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())
