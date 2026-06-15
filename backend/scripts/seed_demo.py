#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random
from django.utils import timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etcash.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Company
from mpesa.models import MpesaConfig, MpesaTransaction

def seed_demo_data():
    print("=" * 50)
    print("Seeding ETcash Demo Data")
    print("=" * 50)

    # Create company with correct field names
    company_data = {
        "name": "Demo Enterprises Ltd",
        "mode": "sme",
        "phone": "+254700123456",
        "kra_pin": "P051234567A",
        "fy_start_month": 1
    }

    company, created = Company.objects.get_or_create(
        name="Demo Enterprises Ltd",
        defaults=company_data
    )
    print(f"✓ Company: {company.name}")
    print(f"  Mode: {company.mode}")
    print(f"  Phone: {company.phone}")
    print(f"  KRA PIN: {company.kra_pin}")

    # Get or create admin
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('Admin1234!')
        admin.save()
        print("✓ Created admin user (password: Admin1234!)")
    else:
        print(f"✓ Admin user exists")

    # Try to import Customer model
    try:
        from invoicing.models import Customer
        has_customer = True
        print("✓ Customer model found")
    except ImportError:
        has_customer = False
        print("⚠ Customer model not found - skipping customer creation")

    # Create M-Pesa config
    try:
        mpesa_config, created = MpesaConfig.objects.get_or_create(
            company=company,
            defaults={
                "business_shortcode": "123456",
                "business_name": "Demo Enterprises",
                "business_type": "PAYBILL",
                "environment": "SANDBOX",
                "auto_reconcile": True,
                "auto_send_stk": True
            }
        )
        print(f"✓ M-Pesa Config: Paybill {mpesa_config.business_shortcode}")
    except Exception as e:
        print(f"⚠ Could not create M-Pesa config: {e}")
        mpesa_config = None

    # Create customers if model exists
    customers = []
    if has_customer:
        customers_data = [
            {"name": "James Mwangi", "phone": "254711223344", "email": "james@example.com"},
            {"name": "Sarah Wanjiku", "phone": "254722334455", "email": "sarah@example.com"},
            {"name": "Peter Omondi", "phone": "254733445566", "email": "peter@example.com"},
        ]
        
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                company=company,
                name=data["name"],
                defaults={"phone": data["phone"]}
            )
            customers.append(customer)
            print(f"✓ Customer: {customer.name} ({customer.phone})")

    # Create sample M-Pesa transactions
    transactions_created = 0

    if mpesa_config:
        print("\nCreating sample M-Pesa transactions...")
        
        for i in range(10):
            if customers:
                customer = random.choice(customers)
                customer_name = customer.name
                customer_phone = customer.phone
                account_ref = f"INV-{i+1:03d}"
            else:
                customer_name = f"Customer {i+1}"
                customer_phone = f"2547{random.randint(10000000, 99999999)}"
                account_ref = f"REF-{i+1:03d}"
            
            amount = Decimal(random.randint(1000, 50000))
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(1, 23)
            # Make timezone-aware datetime
            transaction_date = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            transaction_id = f"MPESA{random.randint(100000000, 999999999)}"
            
            transaction_fields = [f.name for f in MpesaTransaction._meta.get_fields()]
            
            transaction_data = {
                "company": company,
                "transaction_id": transaction_id,
                "amount": amount,
                "customer_phone": customer_phone,
                "business_shortcode": mpesa_config.business_shortcode,
                "account_reference": account_ref,
                "transaction_date": transaction_date,
                "status": "COMPLETED",
            }
            
            if 'customer_name' in transaction_fields:
                transaction_data["customer_name"] = customer_name
            if 'receipt_number' in transaction_fields:
                transaction_data["receipt_number"] = transaction_id
            if 'payment_method' in transaction_fields:
                transaction_data["payment_method"] = "MPESA"
            if 'currency' in transaction_fields:
                transaction_data["currency"] = "KES"
            
            try:
                mpesa_transaction, created = MpesaTransaction.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults=transaction_data
                )
                
                if created:
                    transactions_created += 1
                    print(f"  ✓ {transaction_date.strftime('%Y-%m-%d %H:%M')} - {customer_name} paid KES {amount:,.2f}")
            except Exception as e:
                print(f"  ✗ Error creating transaction {i+1}: {e}")

    # Summary
    total_transactions = 0
    total_amount = 0
    if mpesa_config:
        total_transactions = MpesaTransaction.objects.filter(company=company).count()
        from django.db.models import Sum
        total_amount = MpesaTransaction.objects.filter(company=company, status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0

    print("\n" + "=" * 50)
    print("DEMO DATA SUMMARY")
    print("=" * 50)
    print(f"Company: {company.name}")
    print(f"Company Mode: {company.mode}")
    print(f"KRA PIN: {company.kra_pin}")
    if mpesa_config:
        print(f"M-Pesa Paybill: {mpesa_config.business_shortcode}")
    print(f"M-Pesa Transactions Created: {transactions_created}")
    print(f"Total M-Pesa Transactions in DB: {total_transactions}")
    print(f"Total Amount: KES {total_amount:,.2f}")
    print(f"Total Customers: {len(customers)}")
    print("\nTest Phone Numbers:")
    for customer in customers:
        print(f"  • {customer.name}: {customer.phone}")
    print("\nSample M-Pesa Transaction IDs (for testing):")
    sample_transactions = MpesaTransaction.objects.filter(company=company)[:3]
    for tx in sample_transactions:
        print(f"  • {tx.transaction_id} - KES {tx.amount:,.2f}")
    print("=" * 50)
    print("✓ Demo data seeding complete!")
    print("=" * 50)

if __name__ == "__main__":
    seed_demo_data()
