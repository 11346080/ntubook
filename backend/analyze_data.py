import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
import django
django.setup()

from core.models import Department, ClassGroup

print('CURRENT DATA STRUCTURE ANALYSIS')
print('=' * 100)

# Check departments
print('\nDepartments sample:')
print('-' * 100)
for dept in Department.objects.all()[:10]:
    campus_val = dept.campus_id if dept.campus else 'NULL'
    print(f'ID={dept.id:3} | Campus={str(campus_val):>5} | ProgType={dept.program_type_id:2} | {dept.name_zh:25} | {dept.code}')

total_depts = Department.objects.count()
with_campus = Department.objects.filter(campus__isnull=False).count()
print(f'\nTotal departments: {total_depts}')
print(f'With campus info: {with_campus} ({100*with_campus/total_depts:.1f}%)')
print(f'Campus is NULL: {total_depts - with_campus} ({100*(total_depts-with_campus)/total_depts:.1f}%)')

# Check if ClassGroup has the relationship we need
print('\n\nClassGroup structure analysis:')
print('-' * 100)
for cg in ClassGroup.objects.all()[:5]:
    dept = cg.department
    print(f'ClassGroup: {cg.name_zh}')
    print(f'  -> Department: {dept.name_zh} (ID={dept.id})')
    print(f'  -> Department.campus: {dept.campus} (ID={dept.campus_id})')
    print(f'  -> Department.program_type: {dept.program_type} (ID={dept.program_type_id})')
    print()
