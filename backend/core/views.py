from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.seed import seed_chart_of_accounts

from .models import Company
from .serializers import CompanySerializer, LoginSerializer, SetupSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class SetupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if Company.objects.exists():
            return Response('ETcash is already configured', status=status.HTTP_400_BAD_REQUEST)
        serializer = SetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        company = user.profile.company
        seed_chart_of_accounts(company)
        if company.mode == 'multi_entity':
            from entities.models import LegalEntity
            LegalEntity.objects.get_or_create(
                company=company, code='HQ', defaults={'name': company.name, 'is_default': True},
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'company': CompanySerializer(company).data,
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Logged out.'})


class CompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({})
        return Response(CompanySerializer(profile.company).data)

    def patch(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'No company.'}, status=status.HTTP_400_BAD_REQUEST)
        ser = CompanySerializer(profile.company, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
