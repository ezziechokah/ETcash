from django.urls import path

from .views import SampleInfoView, SampleStatusView

urlpatterns = [
    path('sample/info/', SampleInfoView.as_view()),
    path('sample/status/', SampleStatusView.as_view()),
]
