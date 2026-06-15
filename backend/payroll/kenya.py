"""Simplified Kenya payroll statutory calculations (MVP)."""
from decimal import Decimal


def nhif_monthly(gross):
    """NHIF contribution by gross salary band (simplified 2024 schedule)."""
    g = float(gross)
    bands = [
        (5999, 150), (7999, 300), (11999, 400), (14999, 500),
        (19999, 600), (24999, 750), (29999, 850), (34999, 900),
        (39999, 950), (44999, 1000), (49999, 1100), (59999, 1200),
        (69999, 1300), (79999, 1400), (89999, 1500), (99999, 1600),
    ]
    for limit, amt in bands:
        if g <= limit:
            return Decimal(str(amt))
    return Decimal('1700')


def nssf_employee(gross):
    """NSSF Tier I — 6% of pensionable pay up to 7,000."""
    pensionable = min(gross, Decimal('7000'))
    return (pensionable * Decimal('0.06')).quantize(Decimal('0.01'))


def paye_monthly(taxable):
    """Simplified monthly PAYE bands (KES)."""
    t = taxable
    tax = Decimal('0')
    if t <= Decimal('24000'):
        return Decimal('0')
    if t <= Decimal('32333'):
        tax += (t - Decimal('24000')) * Decimal('0.25')
    elif t <= Decimal('500000'):
        tax += Decimal('2083.25') + (t - Decimal('32333')) * Decimal('0.30')
    else:
        tax += Decimal('150000') + (t - Decimal('500000')) * Decimal('0.325')
    return tax.quantize(Decimal('0.01'))


def compute_payslip(gross_salary):
    gross = Decimal(str(gross_salary))
    personal_relief = Decimal('2400')
    nssf = nssf_employee(gross)
    nhif = nhif_monthly(gross)
    taxable = max(Decimal('0'), gross - nssf - personal_relief)
    paye = paye_monthly(taxable)
    total_deductions = nssf + nhif + paye
    net = gross - total_deductions
    return {
        'gross': gross,
        'nssf': nssf,
        'nhif': nhif,
        'paye': paye,
        'total_deductions': total_deductions,
        'net': net.quantize(Decimal('0.01')),
    }
