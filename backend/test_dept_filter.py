import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
import django
django.setup()

from django.test import RequestFactory
from core.views import department_list_api
from core.models import Department, Campus, ProgramType

print('=' * 80)
print('DEPARTMENT FILTERING TEST')
print('=' * 80)

# Get test data
campuses = list(Campus.objects.all())
program_types = list(ProgramType.objects.all())

if campuses and program_types:
    campus_id = campuses[0].id
    program_type_id = program_types[0].id
    
    print(f'\nTest 1: No filter')
    all_depts = Department.objects.all()
    print(f'  Total departments: {all_depts.count()}')
    
    print(f'\nTest 2: Filter by campus_id={campus_id}')
    by_campus = Department.objects.filter(campus_id=campus_id)
    print(f'  Results: {by_campus.count()}')
    
    print(f'\nTest 3: Filter by program_type_id={program_type_id}')
    by_prog = Department.objects.filter(program_type_id=program_type_id)
    print(f'  Results: {by_prog.count()}')
    
    print(f'\nTest 4: Filter by BOTH campus_id={campus_id} AND program_type_id={program_type_id}')
    by_both = Department.objects.filter(campus_id=campus_id, program_type_id=program_type_id)
    print(f'  Results: {by_both.count()}')
    
    # Test via API
    print(f'\nTest 5: API endpoint /api/core/departments/?campus_id={campus_id}&program_type_id={program_type_id}')
    factory = RequestFactory()
    request = factory.get('/api/core/departments/', {
        'campus_id': str(campus_id),
        'program_type_id': str(program_type_id)
    })
    api_response = department_list_api(request)
    print(f'  API Response: {api_response.data if hasattr(api_response, "data") else "ERROR"}')
    print(f'  Data count: {len(api_response.data) if hasattr(api_response, "data") else "N/A"}')
    
    # Show sample data
    print(f'\nSample departments with both filters:')
    sample = Department.objects.filter(campus_id=campus_id, program_type_id=program_type_id)[:3]
    for dept in sample:
        print(f'  ID={dept.id}, {dept.name_zh}')

print('\n' + '=' * 80)
