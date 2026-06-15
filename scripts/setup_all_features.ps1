# Setup all new features for ETcash
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ETcash - Setting up all new features" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Features to setup
$features = @(
    "M-Pesa Integration",
    "KRA Integration", 
    "WhatsApp Business",
    "Mobile API",
    "Sample Demo Data"
)

Write-Host "Features to be installed:" -ForegroundColor Yellow
foreach ($feature in $features) {
    Write-Host "  • $feature" -ForegroundColor White
}
Write-Host ""

# Confirm
$confirmation = Read-Host "Do you want to proceed? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Setup cancelled." -ForegroundColor Red
    exit
}

# Run migrations for new apps
Write-Host "[1/5] Running database migrations..." -ForegroundColor Yellow
Push-Location backend
.\.venv\Scripts\Activate.ps1
python manage.py makemigrations mpesa kra whatsapp mobile
python manage.py migrate
Pop-Location

# Create Django app directories if not exist
Write-Host "[2/5] Ensuring app directories exist..." -ForegroundColor Yellow
$apps = @("mpesa", "kra", "whatsapp", "mobile")
foreach ($app in $apps) {
    $appPath = "backend/apps/$app"
    if (-not (Test-Path $appPath)) {
        New-Item -ItemType Directory -Path $appPath -Force | Out-Null
        Write-Host "  ✓ Created $app directory"
    }
}

# Seed M-Pesa demo data
Write-Host "[3/5] Seeding M-Pesa demo data..." -ForegroundColor Yellow
Push-Location backend
.\.venv\Scripts\Activate.ps1
python scripts/seed_mpesa_demo_data.py
Pop-Location

# Create WhatsApp templates
Write-Host "[4/5] Creating WhatsApp templates..." -ForegroundColor Yellow
Push-Location backend
.\.venv\Scripts\Activate.ps1
python -c "
import django; django.setup()
from apps.whatsapp.models import WhatsAppTemplate
from django.contrib.auth import get_user_model
from apps.core.models import Company

company = Company.objects.first()
if company:
    templates = [
        {'name': 'invoice_payment', 'category': 'INVOICE', 'content': 'Dear {{customer_name}},\\n\\nPlease find your invoice {{invoice_number}} for KES {{amount}}.\\n\\nDue date: {{due_date}}\\n\\nPay here: {{link}}', 'variables': ['customer_name', 'invoice_number', 'amount', 'due_date', 'link']},
        {'name': 'payment_reminder', 'category': 'PAYMENT_REMINDER', 'content': 'Reminder: Invoice {{invoice_number}} of KES {{amount_due}} is {{days_overdue}} days overdue.\\n\\nPlease pay here: {{link}}', 'variables': ['customer_name', 'invoice_number', 'amount_due', 'days_overdue', 'link']},
        {'name': 'payment_receipt', 'category': 'RECEIPT', 'content': 'Dear {{customer_name}},\\n\\nPayment received for invoice {{invoice_number}}: KES {{amount_paid}}\\n\\nReference: {{mpesa_code}}\\n\\nThank you!', 'variables': ['customer_name', 'invoice_number', 'amount_paid', 'balance', 'payment_date', 'mpesa_code']},
    ]
    for tpl in templates:
        obj, created = WhatsAppTemplate.objects.get_or_create(
            company=company,
            name=tpl['name'],
            defaults={
                'category': tpl['category'],
                'content': tpl['content'],
                'variables': tpl['variables'],
                'is_approved': True,
                'whatsapp_template_id': tpl['name']
            }
        )
        if created:
            print(f'  ✓ Created template: {tpl[\"name\"]}')
"
Pop-Location

Write-Host "[5/5] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "New Features Available:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. M-Pesa Integration"
Write-Host "   • Paybill: 123456 (Demo)"
Write-Host "   • Sample M-Pesa numbers for testing:"
Write-Host "     - James Mwangi: 254711223344"
Write-Host "     - Sarah Wanjiku: 254722334455"
Write-Host "     - Peter Omondi: 254733445566"
Write-Host ""
Write-Host "2. KRA Integration (Demo Mode)"
Write-Host "   • PIN validation for demo PINs:"
Write-Host "     - P051234567A"
Write-Host "     - P061234567B"
Write-Host "     - P071234567C"
Write-Host ""
Write-Host "3. WhatsApp Business"
Write-Host "   • Invoice delivery via WhatsApp"
Write-Host "   • Payment reminders"
Write-Host "   • Payment receipts"
Write-Host ""
Write-Host "4. Mobile API"
Write-Host "   • Mobile-optimized endpoints"
Write-Host "   • Offline data sync"
Write-Host "   • Quick actions"
Write-Host ""
Write-Host "To test M-Pesa payments, send a POST request to:"
Write-Host "POST /api/mpesa/simulate_payment/"
Write-Host '{
  "phone_number": "254711223344",
  "amount": 5000,
  "account_reference": "INV-20241201-001"
}'
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! Restart ETcash to use new features" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan