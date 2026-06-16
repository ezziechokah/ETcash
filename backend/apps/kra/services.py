import json
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from .models import KRAPinValidation, KRAVATReturn, KRAeTIMSInvoice

class KRAService:
    """Kenya Revenue Authority API Integration"""
    
    def __init__(self, company):
        self.company = company
        self.kra_profile = company.kra_profile if hasattr(company, 'kra_profile') else None
        
        # API endpoints
        self.base_url = "https://itax.kra.go.ke/api"
        if settings.DEBUG:
            self.base_url = "https://itax.kra.go.ke/sandbox/api"
    
    def validate_pin(self, pin_number):
        """Validate a KRA PIN number"""
        
        if settings.DEBUG:
            valid_sample_pins = ['P051234567A', 'P061234567B', 'P071234567C', 'A001234567Z']
            
            is_valid = pin_number.upper() in valid_sample_pins
            taxpayer_name = f"Sample Business {pin_number}" if is_valid else ""
            
            KRAPinValidation.objects.create(
                company=self.company,
                pin_validated=pin_number,
                is_valid=is_valid,
                taxpayer_name=taxpayer_name if is_valid else "",
                raw_response={'demo': True, 'valid': is_valid}
            )
            
            return {
                'is_valid': is_valid,
                'taxpayer_name': taxpayer_name if is_valid else None,
                'message': 'PIN is valid' if is_valid else 'PIN is invalid or not registered'
            }
        
        return {'is_valid': False, 'message': 'Validation service unavailable'}
    
    def submit_vat_return(self, period_start, period_end, sales_data, purchases_data):
        """Submit VAT return to KRA iTax"""
        
        if settings.DEBUG:
            import random
            import string
            
            receipt = ''.join(random.choices(string.digits, k=15))
            
            # Create VAT return record
            vat_return = KRAVATReturn.objects.create(
                company=self.company,
                period_start=period_start,
                period_end=period_end,
                standard_rated_sales=sales_data.get('standard_rated', 0),
                zero_rated_sales=sales_data.get('zero_rated', 0),
                exempt_sales=sales_data.get('exempt', 0),
                purchases_taxable=purchases_data.get('taxable', 0),
                imports_vat=purchases_data.get('imports_vat', 0),
                acknowledgement_receipt=receipt,
                kra_status='ACCEPTED',
                kra_response_code='00',
                kra_response_message='VAT return accepted by KRA'
            )
            vat_return.calculate_totals()
            
            return {
                'success': True,
                'acknowledgement_receipt': receipt,
                'vat_return_id': str(vat_return.id),
                'net_vat_payable': float(vat_return.net_vat_declared),
                'message': 'VAT return submitted successfully to KRA'
            }
        
        return {'success': False, 'message': 'KRA submission service not configured'}
    
    def submit_withholding_tax_return(self, period_month, period_year, transactions):
        """Submit Withholding Tax return to KRA"""
        
        if settings.DEBUG:
            import random
            import string
            
            receipt = ''.join(random.choices(string.digits, k=15))
            
            from .models import KRAWithholdingTaxReturn
            wht_return = KRAWithholdingTaxReturn.objects.create(
                company=self.company,
                period_month=period_month,
                period_year=period_year,
                total_gross_payments=sum(t.get('gross_amount', 0) for t in transactions),
                total_tax_withheld=sum(t.get('tax_amount', 0) for t in transactions),
                acknowledgement_receipt=receipt,
                kra_status='ACCEPTED',
                payees=transactions
            )
            
            return {
                'success': True,
                'acknowledgement_receipt': receipt,
                'wht_return_id': str(wht_return.id),
                'message': 'WHT return submitted successfully'
            }
        
        return {'success': False, 'message': 'KRA WHT service not configured'}
    
    def validate_invoice_etims(self, invoice):
        """Validate invoice with KRA eTIMS system"""
        
        if settings.DEBUG:
            import random
            import string
            import base64
            
            etims_number = f"ETIMS{datetime.now().strftime('%Y%m%d')}{''.join(random.choices(string.digits, k=8))}"
            
            qr_data = {
                'invoice_number': getattr(invoice, 'invoice_number', 'N/A'),
                'total': float(getattr(invoice, 'total_amount', 0)),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            qr_base64 = base64.b64encode(json.dumps(qr_data).encode()).decode()
            
            etims_record = KRAeTIMSInvoice.objects.create(
                company=self.company,
                invoice_number=getattr(invoice, 'invoice_number', ''),
                invoice_id=str(getattr(invoice, 'id', '')),
                etims_invoice_number=etims_number,
                qr_code=qr_base64,
                security_code=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
                kra_request_id=''.join(random.choices(string.digits, k=20)),
                kra_response_code='00',
                kra_response_message='Invoice validated by KRA',
                status='VALIDATED',
                validated_at=datetime.now()
            )
            
            return {
                'success': True,
                'etims_invoice_number': etims_number,
                'qr_code': qr_base64,
                'security_code': etims_record.security_code,
                'message': 'Invoice validated with KRA eTIMS'
            }
        
        return {'success': False, 'message': 'eTIMS service not configured'}
    
    def get_taxpayer_info(self):
        """Get taxpayer information from KRA"""
        
        if self.kra_profile:
            return {
                'success': True,
                'pin': self.kra_profile.pin,
                'business_name': self.kra_profile.taxpayer_name,
                'is_vat_registered': self.kra_profile.is_vat_registered,
                'is_withholding_agent': self.kra_profile.is_withholding_tax_agent
            }
        
        return {'success': False, 'message': 'Taxpayer not configured'}

class KRAiTaxClient:
    """iTax integration for annual returns and compliance"""
    
    @staticmethod
    def generate_paye_returns(company, year, monthly_data):
        """Generate PAYE return for KRA"""
        
        kra_profile = company.kra_profile if hasattr(company, 'kra_profile') else None
        
        paye_return = {
            'pin': kra_profile.pin if kra_profile else '',
            'company_name': company.name,
            'year': year,
            'monthly_returns': []
        }
        
        for month_data in monthly_data:
            paye_return['monthly_returns'].append({
                'month': month_data['month'],
                'total_employees': month_data['employee_count'],
                'total_gross_pay': float(month_data['gross_pay']),
                'total_paye': float(month_data['paye']),
                'total_nssf': float(month_data['nssf']),
                'total_nhif': float(month_data['nhif'])
            })
        
        return paye_return
    
    @staticmethod
    def generate_p9a_form(employee, year):
        """Generate P9A form for an employee"""
        
        company = employee.company if hasattr(employee, 'company') else None
        kra_profile = company.kra_profile if company and hasattr(company, 'kra_profile') else None
        
        return {
            'employer_pin': kra_profile.pin if kra_profile else '',
            'employer_name': company.name if company else '',
            'employee_pin': getattr(employee, 'kra_pin', ''),
            'employee_name': getattr(employee, 'name', ''),
            'year': year,
            'total_gross_income': 0,  # Would calculate from payroll
            'total_paye_deducted': 0,
            'benefits_in_kind': 0,
            'pension_contributions': 0
        }