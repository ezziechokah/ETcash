from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Company, UserProfile


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']

    def get_full_name(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.full_name if profile else ''


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'mode', 'kra_pin', 'phone', 'fy_start_month']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not hasattr(user, 'profile'):
            raise serializers.ValidationError('Account not linked to a company')
        attrs['user'] = user
        return attrs


class SetupSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField()
    kra_pin = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    fy_start_month = serializers.IntegerField(min_value=1, max_value=12, default=1)
    mode = serializers.ChoiceField(choices=['freelancer', 'sme', 'multi_entity'])

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken')
        return value

    def create(self, validated_data):
        if Company.objects.exists():
            raise serializers.ValidationError('ETcash is already set up')

        company = Company.objects.create(
            name=validated_data['company_name'],
            mode=validated_data['mode'],
            kra_pin=validated_data.get('kra_pin', ''),
            phone=validated_data.get('phone', ''),
            fy_start_month=validated_data.get('fy_start_month', 1),
        )
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        UserProfile.objects.create(
            user=user,
            company=company,
            full_name=validated_data.get('full_name', ''),
        )
        return user
