#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
import os
from election.models import Student
adm = int(os.environ.get('ADMIN_ADM'))
pwd = os.environ.get('ADMIN_PASS')
if not Student.objects.filter(admission_number=adm).exists():
    Student.objects.create_superuser(
        admission_number=adm,
        password=pwd,
        first_name='Admin',
        last_name='User',
        email='admin@kuravote.com'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"