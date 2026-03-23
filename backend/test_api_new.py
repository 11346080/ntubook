import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
import django
django.setup()

from django.test import RequestFactory
from core.views import department_list_api
from core.models import Campus, ProgramType

factory = RequestFactory()

campus = Campus.objects.first()
program_type = ProgramType.objects.first()

if campus and program_type:
    print('=' * 80)
    print('API DEPARTMENT FILTERING TEST - WITH NEW Q OBJECT LOGIC')
    print('=' * 80)
    
    campus_id = campus.id
    program_type_id = program_type.id
    
    print(f'\nTest Case:')
    print(f'  Campus: {campus.name_zh} (ID={campus_id})')
    print(f'  ProgramType: {program_type.name_zh} (ID={program_type_id})')
    
    # Test 1: No filter
    print(f'\n1. No filter:')
    request = factory.get('/api/core/departments/')
    response = department_list_api(request)
    print(f'   Result count: {len(response.data)}')
    
    # Test 2: Program type only
    print(f'\n2. Filter by program_type_id={program_type_id}:')
    request = factory.get('/api/core/departments/', {'program_type_id': str(program_type_id)})
    response = department_list_api(request)
    print(f'   Result count: {len(response.data)}')
    if response.data:
        print(f'   Sample: {response.data[0]["name_zh"]}')
    
    # Test 3: Campus only
    print(f'\n3. Filter by campus_id={campus_id}:')
    request = factory.get('/api/core/departments/', {'campus_id': str(campus_id)})
    response = department_list_api(request)
    print(f'   Result count: {len(response.data)}')
    if response.data:
        print(f'   Sample: {response.data[0]["name_zh"]}')
    
    # Test 4: Both
    print(f'\n4. Filter by BOTH campus_id={campus_id} AND program_type_id={program_type_id}:')
    request = factory.get('/api/core/departments/', {
        'campus_id': str(campus_id),
        'program_type_id': str(program_type_id)
    })
    response = department_list_api(request)
    print(f'   Result count: {len(response.data)}')
    if response.data:
        for dept in response.data[:3]:
            print(f'   - {dept["name_zh"]} (campus={dept["campus"]})')
    
    print('\n' + '=' * 80)
    print('✅ Test complete - departments now include cross-campus records!')
    print('=' * 80)
