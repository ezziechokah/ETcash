@echo off
echo ========================================
echo ETcash - New Company Setup
echo ========================================

set /p company_name="Company Name: "
set /p phone="Phone Number: "
set /p kra_pin="KRA PIN: "
set /p mode="Mode (freelancer/sme/multi_entity): "

echo.
echo Creating company...
python manage.py shell -c "
from core.models import Company, UserProfile
from django.contrib.auth.models import User

company = Company.objects.create(
    name='%company_name%',
    phone='%phone%',
    kra_pin='%kra_pin%',
    mode='%mode%',
    fy_start_month=1
)

admin = User.objects.get(username='admin')
profile, _ = UserProfile.objects.get_or_create(user=admin)
profile.company = company
profile.save()

print('Company created successfully!')
"

echo.
echo Company setup complete!
echo Default login: admin / Admin1234!
pause