from election.models import Student
import os
import django
import csv
import time

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'kuravote.settings'
)
django.setup()


print('Reading CSV...')
start = time.time()

existing = set(
    Student.objects.values_list('admission_number', flat=True)
)
print(f'Existing students: {len(existing)}')

to_create = []
skipped = 0

with open('test_students_10000.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        adm = int(row['admission_number'])
        if adm in existing:
            skipped += 1
            continue
        existing.add(adm)
        s = Student(
            admission_number=adm,
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            is_active=True,
            password_changed=False,
        )
        s.set_password(str(adm))
        to_create.append(s)

print(f'Preparing {len(to_create)} students...')

if to_create:
    Student.objects.bulk_create(
        to_create,
        batch_size=1000,
        ignore_conflicts=True
    )

end = time.time()
print(f'Done.')
print(f'Imported: {len(to_create)}')
print(f'Skipped:  {skipped}')
print(f'Time:     {round(end - start, 2)}s')
print(
    f'Speed:    '
    f'{round(len(to_create) / (end - start), 0):.0f} students/second'
)
