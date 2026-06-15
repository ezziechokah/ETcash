#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etcash.settings')
django.setup()

# Import models without 'apps.' prefix
from django.contrib.auth.models import User
from core.models import Company
from mpesa.models import MpesaConfig, MpesaTransaction, MpesaSTKPush
from invoicing.models import Customer, Invoice, InvoiceLine

def seed_mpesa_demo_data():
    print("=" * 50)
    print("Seeding M-Pesa Demo Data")
    print("=" * 50)
    
    # Get or create company
    company, created = Company.objects.get_or_create(
        name="Demo Enterprises Ltd",
        defaults={
            "email": "demo@demoenterprises.co.ke",
            "phone": "+254700123456",
            "address": "Nairobi, Kenya"
        }
    )
    
    if created:
        print(f"✓ Created company: {company.name}")
    else:
        print(f"✓ Using existing company: {company.name}")
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'Admin1234!')
        print("✓ Created admin user")
    else:
        print(f"✓ Using existing admin: {admin.username}")
    
    # Create M-Pesa config
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
    
    if created:
        print(f"✓ Created M-Pesa Config: {mpesa_config.business_name} (Paybill: {mpesa_config.business_shortcode})")
    else:
        print(f"✓ Using existing M-Pesa Config: Paybill {mpesa_config.business_shortcode}")
    
    # Create sample customers
    customers = []
    sample_data = [
        {"name": "James Mwangi", "phone": "254711223344", "email": "james@example.com"},
        {"name": "Sarah Wanjiku", "phone": "254722334455", "email": "sarah@example.com"},
        {"name": "Peter Omondi", "phone": "254733445566", "email": "peter@example.com"},
        {"name": "Mary Akinyi", "phone": "254744556677", "email": "mary@example.com"},
        {"name": "John Kamau", "phone": "254755667788", "email": "john@example.com"},
    ]
    
    for data in sample_data:
        customer, created = Customer.objects.get_or_create(
            company=company,
            name=data["name"],
            defaults={"phone": data["phone"], "email": data["email"]}
        )
        customers.append(customer)
        if created:
            print(f"✓ Created customer: {customer.name} ({customer.phone})")
    
    print(f"\n✓ Total customers: {len(customers)}")
    
    # Create sample transactions for the last 30 days
    today = datetime.now()
    transactions_created = 0
    
    print("\nCreating sample M-Pesa transactions...")
    
    for i in range(20):  # Create 20 sample transactions
        customer = random.choice(customers)
        amount = Decimal(random.randint(1000, 50000))
        days_ago = random.randint(0, 30)
        transaction_date = today - timedelta(days=days_ago, hours=random.randint(1, 23))
        
        # Create invoice number
        invoice_number = f"INV-{transaction_date.strftime('%Y%m%d')}-{i+1:03d}"
        
        # Create invoice
        invoice, created = Invoice.objects.get_or_create(
            company=company,
            invoice_number=invoice_number,
            defaults={
                "customer": customer,
                "issue_date": transaction_date.date(),
                "due_date": (transaction_date + timedelta(days=30)).date(),
                "subtotal": amount,
                "total_amount": amount,
                "status": "PAID" if random.random() > 0.3 else "SENT",
                "created_by": admin
            }
        )
        
        # Add line item if invoice was just created
        if created:
            InvoiceLine.objects.create(
                invoice=invoice,
                description="Product/Service Purchase",
                quantity=1,
                unit_price=amount,
                total=amount
            )
        
        # Create M-Pesa transaction
        transaction_id = f"MPESA{random.randint(100000000, 999999999)}"
        
        mpesa_transaction, created = MpesaTransaction.objects.get_or_create(
            transaction_id=transaction_id,
            defaults={
                "company": company,
                "amount": amount,
                "customer_phone": customer.phone,
                "customer_name": customer.name,
                "business_shortcode": mpesa_config.business_shortcode,
                "account_reference": invoice_number,
                "transaction_date": transaction_date,
                "status": "COMPLETED",
                "linked_invoice": invoice if invoice.status == "PAID" else None
            }
        )
        
        if created:
            transactions_created += 1
            print(f"  ✓ {transaction_date.strftime('%Y-%m-%d %H:%M')} - {customer.name} paid KES {amount:,.2f} (Ref: {transaction_id})")
    
    # Create some STK Push records
    print("\nCreating STK Push records...")
    stk_created = 0
    
    for i in range(10):
        customer = random.choice(customers)
        amount = Decimal(random.randint(5000, 30000))
        
        # Create pending invoice
        invoice_number = f"STK-INV-{today.strftime('%Y%m%d')}-{i+1:03d}"
        
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            invoice_number=invoice_number,
            issue_date=today.date(),
            due_date=(today + timedelta(days=30)).date(),
            subtotal=amount,
            total_amount=amount,
            status="SENT",
            created_by=admin
        )
        
        InvoiceLine.objects.create(
            invoice=invoice,
            description="STK Push Payment Request",
            quantity=1,
            unit_price=amount,
            total=amount
        )
        
        # Create STK Push
        checkout_id = f"CHECKOUT{random.randint(100000000, 999999999)}"
        merchant_id = f"MERCHANT{random.randint(100000000, 999999999)}"
        
        stk_push, created = MpesaSTKPush.objects.get_or_create(
            checkout_request_id=checkout_id,
            defaults={
                "company": company,
                "invoice": invoice,
                "phone_number": customer.phone,
                "amount": amount,
                "account_reference": invoice_number,
                "transaction_description": f"Payment for {invoice_number}",
                "merchant_request_id": merchant_id,
                "status": random.choice(["PENDING", "SUCCESS", "FAILED"]),
            }
        )
        
        if created:
            stk_created += 1
            print(f"  ✓ STK Push to {customer.name}: KES {amount:,.2f} - Status: {stk_push.status}")
    
    # Summary
    total_transactions = MpesaTransaction.objects.filter(company=company).count()
    total_amount = MpesaTransaction.objects.filter(company=company, status='COMPLETED').aggregate(total=models.Sum('amount'))['total'] or 0
    
    print("\n" + "=" * 50)
    print("DEMO DATA SUMMARY")
    print("=" * 50)
    print(f"Company: {company.name}")
    print(f"M-Pesa Paybill: {mpesa_config.business_shortcode}")
    print(f"M-Pesa Transactions Created: {transactions_created}")
    print(f"Total M-Pesa Transactions: {total_transactions}")
    print(f"Total Amount: KES {total_amount:,.2f}")
    print(f"STK Push Records Created: {stk_created}")
    print(f"Total Customers: {len(customers)}")
    print("\nSample M-Pesa Numbers for Testing:")
    for customer in customers:
        print(f"  • {customer.name}: {customer.phone}")
    print("=" * 50)
    print("✓ Demo data seeding complete!")
    print("=" * 50)

if __name__ == "__main__":
    import django.db.models as models
    seed_mpesa_demo_data()