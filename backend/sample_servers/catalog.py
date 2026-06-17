"""
Sample data catalog for ETcash demo / development.

All values here stand in for real company, customer, and integration data
until production credentials and records are provided.
"""

# ── Company & admin ──────────────────────────────────────────────────────────

SAMPLE_COMPANY = {
    'name': 'Demo Enterprises Ltd',
    'mode': 'sme',
    'kra_pin': 'P051234567A',
    'phone': '+254 700 123456',
    'fy_start_month': 1,
}

SAMPLE_ADMIN = {
    'username': 'admin',
    'email': 'admin@demoenterprises.co.ke',
    'password': 'Admin1234!',
    'full_name': 'System Administrator',
}

# ── Customers ────────────────────────────────────────────────────────────────

SAMPLE_CUSTOMERS = [
    {'name': 'Acme Kenya Ltd', 'email': 'billing@acme.co.ke', 'phone': '+254 700 123456', 'kra_pin': 'P051234567X'},
    {'name': 'James Mwangi', 'email': 'james@example.com', 'phone': '+254 711 223344', 'kra_pin': 'A001234567B'},
    {'name': 'Sarah Wanjiku', 'email': 'sarah@example.com', 'phone': '+254 722 334455', 'kra_pin': ''},
    {'name': 'Peter Omondi', 'email': 'peter@example.com', 'phone': '+254 733 445566', 'kra_pin': ''},
    {'name': 'Nairobi Tech Solutions', 'email': 'accounts@nairobitech.co.ke', 'phone': '+254 744 556677', 'kra_pin': 'P061234567B'},
]

# ── Vendors ──────────────────────────────────────────────────────────────────

SAMPLE_VENDORS = [
    {'name': 'Office Supplies Kenya', 'email': 'orders@officesupplies.co.ke', 'phone': '+254 720 111222', 'kra_pin': 'P059999999X'},
    {'name': 'Safaricom Business', 'email': 'enterprise@safaricom.co.ke', 'phone': '+254 722 000111', 'kra_pin': 'P071234567C'},
    {'name': 'Legal Partners LLP', 'email': 'billing@legalpartners.co.ke', 'phone': '+254 733 222333', 'kra_pin': 'P081234567D'},
]

# ── Bank accounts ────────────────────────────────────────────────────────────

SAMPLE_BANK_ACCOUNTS = [
    {'name': 'Main Operating Account', 'bank_name': 'KCB Bank', 'account_number': '1234567890', 'opening_balance': '850000.00'},
    {'name': 'M-Pesa Float', 'bank_name': 'Safaricom', 'account_number': '123456', 'opening_balance': '45000.00'},
    {'name': 'USD Reserve', 'bank_name': 'Equity Bank', 'account_number': '9876543210', 'currency': 'USD', 'opening_balance': '5000.00'},
]

# ── Inventory ────────────────────────────────────────────────────────────────

SAMPLE_INVENTORY = [
    {'sku': 'SKU-001', 'name': 'Network Switch 24-port', 'quantity_on_hand': 5, 'unit_cost': '12000', 'selling_price': '18000', 'reorder_level': 2},
    {'sku': 'SKU-002', 'name': 'Laptop Dell Latitude', 'quantity_on_hand': 12, 'unit_cost': '65000', 'selling_price': '85000', 'reorder_level': 3},
    {'sku': 'SKU-003', 'name': 'Office Chair Ergonomic', 'quantity_on_hand': 8, 'unit_cost': '8500', 'selling_price': '12000', 'reorder_level': 2},
]

# ── Payroll ──────────────────────────────────────────────────────────────────

SAMPLE_EMPLOYEES = [
    {'employee_number': 'EMP-001', 'full_name': 'Jane Wanjiku', 'basic_salary': '85000', 'kra_pin': 'A001234567B', 'department': 'Finance'},
    {'employee_number': 'EMP-002', 'full_name': 'David Kamau', 'basic_salary': '120000', 'kra_pin': 'A002234567C', 'department': 'Engineering'},
    {'employee_number': 'EMP-003', 'full_name': 'Grace Akinyi', 'basic_salary': '65000', 'kra_pin': 'A003234567D', 'department': 'Operations'},
]

# ── Projects ─────────────────────────────────────────────────────────────────

SAMPLE_PROJECTS = [
    {'code': 'PRJ-001', 'name': 'Nairobi Office Fit-out', 'client_name': 'Acme Kenya Ltd', 'budget': '500000', 'status': 'in_progress'},
    {'code': 'PRJ-002', 'name': 'ERP Migration', 'client_name': 'Nairobi Tech Solutions', 'budget': '1200000', 'status': 'planning'},
]

# ── M-Pesa (Safaricom sandbox stand-in) ──────────────────────────────────────

SAMPLE_MPESA = {
    'business_shortcode': '174379',
    'business_name': 'Demo Enterprises',
    'business_type': 'PAYBILL',
    'environment': 'SANDBOX',
    'auto_reconcile': True,
    'auto_send_stk': True,
}

# ── KRA (iTax sandbox stand-in) ──────────────────────────────────────────────

SAMPLE_KRA = {
    'pin': 'P051234567A',
    'taxpayer_name': 'Demo Enterprises Ltd',
    'is_vat_registered': True,
    'is_withholding_tax_agent': True,
}

VALID_KRA_PINS = ['P051234567A', 'P061234567B', 'P071234567C', 'A001234567Z']

# ── Legal entities (multi-entity mode) ───────────────────────────────────────

SAMPLE_LEGAL_ENTITIES = [
    {'code': 'HQ', 'name': 'Demo Enterprises Ltd (HQ)', 'kra_pin': 'P051234567A', 'is_default': True},
    {'code': 'NBI', 'name': 'Demo Nairobi Branch', 'kra_pin': 'P061234567B', 'is_default': False},
    {'code': 'MSA', 'name': 'Demo Mombasa Branch', 'kra_pin': 'P071234567C', 'is_default': False},
]
