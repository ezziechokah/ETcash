import json
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from .models import KRAPinValidation, KRAVATReturn, KRAeTIMSInvoice

class KRAService:
    """Kenya Revenue Authority API Integration"""
    
    def __init__(self, company):
        self.company = company
        self.kra_profile = company.kra_profile if hasattr(company, 'kra_profile') else None
        
        # API endpoints (from KRA documentation)
        self.base_url = "https://itax.kra.go.ke/api"  # Production
        if settings.DEBUG:
            self.base_url = "https://itax.kra.go.ke/sandbox/api"  # Sandbox
    
    def validate_pin(self, pin_number):
        """Validate a KRA PIN number"""
        
        # For demo/sample, simulate validation
        if settings.DEBUG:
            # Sample valid PINs for demo
            valid_sample_pins = ['P051234567A', 'P061234567B', 'P071234567C', 'A001234567Z']
            
            is_valid = pin_number.upper() in valid_sample_pins
            taxpayer_name = f"Sample Business {pin_number}" if is_valid else ""
            
            # Record validation
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
        
        # In production, actual API call:
        """
        url = f"{self.base_url}/validatePin"
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
        payload = {'pin': pin_number}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'is_valid': data.get('valid', False),
                'taxpayer_name': data.get('businessName'),
                'message': data.get('message')
            }
        """
        
        return {'is_valid': False, 'message': 'Validation service unavailable'}
    
    def submit_vat_return(self, vat_return):
        """Submit VAT return to KRA iTax"""
        
        # Prepare VAT return data
        vat_data = {
            'pin': self.kra_profile.pin if self.kra_profile else '',
            'period_start': vat_return.period_start.strftime('%Y-%m-%d'),
            'period_end': vat_return.period_end.strftime('%Y-%m-%d'),
            'sales': {
                'standard_rated': float(vat_return.standard_rated_sales),
                'zero_rated': float(vat_return.zero_rated_sales),
                'exempt': float(vat_return.exempt_sales),
                'vat': float(vat_return.standard_rated_vat)
            },
            'purchases': {
                'taxable': float(vat_return.purchases_taxable),
                'vat': float(vat_return.purchases_vat),
                'imports_vat': float(vat_return.imports_vat)
            },
            'net_vat_payable': float(vat_return.net_vat_payable)
        }
        
        # For demo, simulate submission
        if settings.DEBUG:
            import random
            import string
            
            receipt = ''.join(random.choices(string.digits, k=15))
            
            kra_return = KRAVATReturn.objects.create(
                company=self.company,
                vat_return=vat_return,
                sales_vat_declared=vat_return.standard_rated_vat,
                purchases_vat_declared=vat_return.purchases_vat,
                net_vat_declared=vat_return.net_vat_payable,
                acknowledgement_receipt=receipt,
                kra_status='ACCEPTED',
                kra_response_code='00',
                kra_response_message='VAT return accepted by KRA',
                kra_response_data={'receipt': receipt, 'submission_data': vat_data}
            )
            
            return {
                'success': True,
                'acknowledgement_receipt': receipt,
                'message': 'VAT return submitted successfully to KRA'
            }
        
        return {'success': False, 'message': 'KRA submission service not configured'}
    
    def submit_withholding_tax_return(self, period_month, period_year, transactions):
        """Submit Withholding Tax return to KRA"""
        
        wht_data = {
            'pin': self.kra_profile.pin if self.kra_profile else '',
            'period': f"{period_month:02d}/{period_year}",
            'transactions': []
        }
        
        for tx in transactions:
            wht_data['transactions'].append({
                'payee_pin': tx.get('payee_pin'),
                'payee_name': tx.get('payee_name'),
                'payment_date': tx.get('payment_date'),
                'gross_amount': float(tx.get('gross_amount', 0)),
                'tax_rate': float(tx.get('rate', 0)),
                'tax_amount': float(tx.get('tax_amount', 0)),
                'invoice_number': tx.get('invoice_number', '')
            })
        
        # For demo, simulate success
        if settings.DEBUG:
            import random
            import string
            
            receipt = ''.join(random.choices(string.digits, k=15))
            
            return {
                'success': True,
                'acknowledgement_receipt': receipt,
                'message': 'WHT return submitted successfully'
            }
        
        return {'success': False, 'message': 'KRA WHT service not configured'}
    
    def validate_invoice_etims(self, invoice):
        """Validate invoice with KRA eTIMS system"""
        
        # Prepare invoice data for eTIMS
        invoice_data = {
            'pin': self.kra_profile.pin if self.kra_profile else '',
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.issue_date.strftime('%Y-%m-%d'),
            'customer_pin': invoice.customer.tax_pin if invoice.customer.tax_pin else '',
            'customer_name': invoice.customer.name,
            'total_amount': float(invoice.total_amount),
            'vat_amount': float(invoice.vat_amount),
            'items': []
        }
        
        for line in invoice.lines.all():
            invoice_data['items'].append({
                'description': line.description,
                'quantity': float(line.quantity),
                'unit_price': float(line.unit_price),
                'vat_rate': float(line.vat_rate),
                'total': float(line.total)
            })
        
        # For demo, generate eTIMS response
        if settings.DEBUG:
            import random
            import string
            import base64
            
            etims_number = f"ETIMS{datetime.now().strftime('%Y%m%d')}{''.join(random.choices(string.digits, k=8))}"
            
            # Generate fake QR code data
            qr_data = {
                'invoice_number': invoice.invoice_number,
                'pin': self.kra_profile.pin if self.kra_profile else '',
                'total': float(invoice.total_amount),
                'date': invoice.issue_date.strftime('%Y-%m-%d')
            }
            qr_base64 = base64.b64encode(json.dumps(qr_data).encode()).decode()
            
            etims_record = KRAeTIMSInvoice.objects.create(
                company=self.company,
                invoice=invoice,
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

class KRAiTaxClient:
    """iTax integration for annual returns and compliance"""
    
    @staticmethod
    def generate_paye_returns(company, year, monthly_data):
        """Generate PAYE return for KRA"""
        
        # Format data for iTax
        paye_return = {
            'pin': company.kra_profile.pin if hasattr(company, 'kra_profile') else '',
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
        
        return {
            'employer_pin': employee.company.kra_profile.pin if hasattr(employee.company, 'kra_profile') else '',
            'employee_pin': employee.kra_pin,
            'employee_name': employee.name,
            'year': year,
            'total_gross_income': float(employee.total_gross_income_for_year(year)),
            'total_paye_deducted': float(employee.total_paye_deducted_for_year(year)),
            'benefits_in_kind': float(employee.benefits_in_kind_for_year(year) or 0),
            'pension_contributions': float(employee.pension_contributions_for_year(year) or 0)
        }