from django.urls import path

from .views import CompanyView, LoginView, LogoutView, SetupView

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/setup/', SetupView.as_view()),
    path('core/company/', CompanyView.as_view()),
]
