from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from .models import KRATaxpayer, KRAPinValidation, KRAVATReturn
import random
import string

# Simple test view - no auth required
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def kra_test(request):
    """Simple test endpoint for KRA"""
    return JsonResponse({
        'status': 'ok',
        'message': 'KRA app is working!',
        'method': request.method,
        'endpoints': [
            '/api/kra/validate_pin/ - POST (pin)',
            '/api/kra/setup_taxpayer/ - POST (pin, taxpayer_name)',
            '/api/kra/taxpayer_profile/ - GET',
            '/api/kra/submit_vat_return/ - POST (period_start, period_end, sales_vat, purchases_vat, net_vat)',
            '/api/kra/vat_returns/ - GET'
        ]
    })

# PIN Validation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_pin(request):
    """Validate a KRA PIN"""
    try:
        pin = request.data.get('pin')
        
        if not pin:
            return Response({'error': 'PIN is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get company
        company = None
        if hasattr(request.user, 'profile') and request.user.profile:
            company = request.user.profile.company
        
        if not company:
            from core.models import Company
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate PIN (demo mode)
        valid_pins = ['P051234567A', 'P061234567B', 'P071234567C', 'A001234567Z']
        is_valid = pin.upper() in valid_pins
        
        # Record validation - remove taxpayer_status field
        KRAPinValidation.objects.create(
            company=company,
            pin_validated=pin,
            is_valid=is_valid,
            taxpayer_name=f"Sample Business {pin}" if is_valid else "",
            # taxpayer_status removed - this field doesn't exist in the model
        )
        
        return Response({
            'is_valid': is_valid,
            'taxpayer_name': f"Sample Business {pin}" if is_valid else None,
            'message': 'PIN is valid' if is_valid else 'PIN is invalid or not registered'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Setup Taxpayer
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_taxpayer(request):
    """Setup KRA taxpayer profile"""
    try:
        company = None
        if hasattr(request.user, 'profile') and request.user.profile:
            company = request.user.profile.company
        
        if not company:
            from core.models import Company
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=status.HTTP_404_NOT_FOUND)
        
        pin = request.data.get('pin')
        taxpayer_name = request.data.get('taxpayer_name')
        
        if not pin or not taxpayer_name:
            return Response({'error': 'pin and taxpayer_name are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        taxpayer, created = KRATaxpayer.objects.update_or_create(
            company=company,
            defaults={
                'pin': pin,
                'taxpayer_name': taxpayer_name,
                'is_vat_registered': request.data.get('is_vat_registered', False),
                'is_withholding_tax_agent': request.data.get('is_withholding_tax_agent', False)
            }
        )
        
        return Response({
            'success': True,
            'created': created,
            'taxpayer': {
                'id': str(taxpayer.id),
                'pin': taxpayer.pin,
                'taxpayer_name': taxpayer.taxpayer_name,
                'is_vat_registered': taxpayer.is_vat_registered
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get Taxpayer Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def taxpayer_profile(request):
    """Get KRA taxpayer profile"""
    try:
        company = None
        if hasattr(request.user, 'profile') and request.user.profile:
            company = request.user.profile.company
        
        if not company:
            from core.models import Company
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            taxpayer = KRATaxpayer.objects.get(company=company)
            return Response({
                'id': str(taxpayer.id),
                'pin': taxpayer.pin,
                'taxpayer_name': taxpayer.taxpayer_name,
                'is_vat_registered': taxpayer.is_vat_registered,
                'is_withholding_tax_agent': taxpayer.is_withholding_tax_agent,
                'created_at': taxpayer.created_at
            })
        except KRATaxpayer.DoesNotExist:
            return Response({'configured': False, 'message': 'No taxpayer profile found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Submit VAT Return
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_vat_return(request):
    """Submit VAT return to KRA"""
    try:
        company = None
        if hasattr(request.user, 'profile') and request.user.profile:
            company = request.user.profile.company
        
        if not company:
            from core.models import Company
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=status.HTTP_404_NOT_FOUND)
        
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        
        if not period_start or not period_end:
            return Response({'error': 'period_start and period_end are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        receipt = ''.join(random.choices(string.digits, k=15))
        
        vat_return = KRAVATReturn.objects.create(
            company=company,
            period_start=period_start,
            period_end=period_end,
            sales_vat_declared=request.data.get('sales_vat', 0),
            purchases_vat_declared=request.data.get('purchases_vat', 0),
            net_vat_declared=request.data.get('net_vat', 0),
            acknowledgement_receipt=receipt,
            status='ACCEPTED'
        )
        
        return Response({
            'success': True,
            'vat_return_id': str(vat_return.id),
            'acknowledgement_receipt': receipt,
            'message': 'VAT return submitted successfully'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get VAT Returns
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vat_returns(request):
    """Get list of VAT returns"""
    try:
        company = None
        if hasattr(request.user, 'profile') and request.user.profile:
            company = request.user.profile.company
        
        if not company:
            from core.models import Company
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=status.HTTP_404_NOT_FOUND)
        
        vat_returns = KRAVATReturn.objects.filter(company=company).order_by('-period_start')
        
        data = []
        for vr in vat_returns:
            data.append({
                'id': str(vr.id),
                'period_start': vr.period_start,
                'period_end': vr.period_end,
                'sales_vat_declared': float(vr.sales_vat_declared),
                'purchases_vat_declared': float(vr.purchases_vat_declared),
                'net_vat_declared': float(vr.net_vat_declared),
                'status': vr.status,
                'submission_date': vr.submission_date,
                'acknowledgement_receipt': vr.acknowledgement_receipt
            })
        
        return Response({
            'count': len(data),
            'results': data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
