import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
import django
django.setup()

from core.models import Department, Campus, ProgramType

print('=' * 80)
print('DEPARTMENTS DATA CHECK')
print('=' * 80)

# Check totals
total = Department.objects.count()
with_campus = Department.objects.filter(campus__isnull=False).count()
without_campus = Department.objects.filter(campus__isnull=True).count()

print(f'\nTotal records: {total}')
print(f'With campus: {with_campus}')
print(f'Without campus (NULL): {without_campus}')
print(f'Percentage with campus: {100 * with_campus / total if total > 0 else 0:.1f}%')

# Check by campus
print('\nDepartments count by campus:')
for campus in Campus.objects.all():
    count = Department.objects.filter(campus=campus).count()
    print(f'  {campus.name_zh}: {count} records')

# Sample with campus
print('\nSample departments WITH campus:')
for dept in Department.objects.filter(campus__isnull=False)[:5]:
    print(f'  ID={dept.id}, Campus={dept.campus.name_zh}, ProgramType={dept.program_type.name_zh}, Dept={dept.name_zh}')

# Sample without campus
print('\nSample departments WITHOUT campus (NULL):')
for dept in Department.objects.filter(campus__isnull=True)[:5]:
    prog_name = dept.program_type.name_zh if dept.program_type else 'NONE'
    print(f'  ID={dept.id}, Campus=NULL, ProgramType={prog_name}, Dept={dept.name_zh}')

# Check program type distribution
print('\nDistribution across program types:')
for prog_type in ProgramType.objects.all()[:5]:
    dept_count = Department.objects.filter(program_type=prog_type).count()
    with_campus_count = Department.objects.filter(program_type=prog_type, campus__isnull=False).count()
    print(f'  {prog_type.name_zh}: {dept_count} total, {with_campus_count} with campus')

print('=' * 80)
