from django.urls import path
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({'status': 'ok', 'message': 'KRA app is working!'})

urlpatterns = [
    path('test/', test_view, name='test'),
]
