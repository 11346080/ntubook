"""
Seed student number rules for 4-year, 2-year, and 5-year programs.

Usage:
    python manage.py seed_student_number_rules

Each StudentNumberRule row = (program_type_id, department_id).
The regex stored in 'note' shows the 2-digit dept_code in student numbers,
but DB departments.code uses a different 3-digit scheme (e.g. 41 → 401).
The mapping below converts between the two.

IMPORTANT:
  - For 4-year (program_type code='4'):   dept_code = 2 digits (e.g. 41, 4A)
  - For 2-year (program_type code='3'):   dept_code = 2 digits (e.g. 31, 3B)
  - For 5-year (program_type code='7'):   dept_code = 2 digits (e.g. 51, 56)
    Note: DB uses code='7' for 五專, NOT '5'.
"""
from django.core.management.base import BaseCommand
from core.models import ProgramType, Department, StudentNumberRule


class Command(BaseCommand):
    help = 'Seed student number rules for 4-year, 2-year, and 5-year programs'

    def handle(self, *args, **options):
        # ── 四技日間部 (program_type code='4') ────────────────────
        pt4 = ProgramType.objects.get(code='4')
        four_year_rules = [
            # (dept_code, DB departments.code, 系所名稱)
            ('41', '401', '會計資訊系'),
            ('42', '402', '財務金融系'),
            ('43', '403', '財政稅務系'),
            ('44', '404', '國際商務系'),
            ('45', '405', '企業管理系'),
            ('46', '406', '資訊管理系'),
            ('47', '407', '應用外語系'),
            ('4A', '40A', '商業設計管理系'),
            ('4B', '40B', '創意科技與產品設計系'),
            ('4C', '40C', '數位多媒體設計系'),
        ]
        for dept_code, db_code, name in four_year_rules:
            self._upsert(pt4, dept_code, db_code, name)

        self.stdout.write('')

        # ── 二技日間部 (program_type code='3') ────────────────────
        pt3 = ProgramType.objects.get(code='3')
        two_year_rules = [
            ('31', '301', '會計資訊系'),
            ('32', '302', '財務金融系'),
            ('33', '303', '財政稅務系'),
            ('34', '304', '國際商務系'),
            ('35', '305', '企業管理系'),
            ('36', '306', '資訊管理系'),
            ('37', '307', '應用外語系'),
            ('3A', '30A', '商業設計管理系'),
            ('3B', '30B', '創意科技與產品設計系'),
        ]
        for dept_code, db_code, name in two_year_rules:
            self._upsert(pt3, dept_code, db_code, name)

        self.stdout.write('')

        # ── 五專日間部 (program_type code='7') ─────────────────────
        # dept_code 依用戶確認的學號規則處理：
        #   52→521, 51→508, 53→503, 54→504, 55→505, 56→506, 57→509
        # 已排除 code='500'（通識）及 code='902'（體育）。
        pt5 = ProgramType.objects.get(code='7')
        five_year_rules = [
            ('51', '521', '會計與資料科學科'),
            ('52', '508', '財務金融科'),
            ('53', '503', '財政稅務科'),
            ('54', '504', '國際貿易科'),
            ('55', '505', '企業管理科'),
            ('56', '506', '資訊管理科'),
            ('57', '509', '應用外語科'),
        ]
        for dept_code, db_code, name in five_year_rules:
            self._upsert(pt5, dept_code, db_code, name)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. 4-year: {len(four_year_rules)}, '
            f'2-year: {len(two_year_rules)}, '
            f'5-year: {len(five_year_rules)}'
        ))

    def _upsert(self, program_type, dept_code, db_code, dept_name):
        try:
            department = Department.objects.get(program_type=program_type, code=db_code)
        except Department.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                f'  [SKIP] dept_code={dept_code} ({dept_name}): '
                f'Department(code={db_code!r}, program_type={program_type.code!r}) '
                f'not found in DB.'
            ))
            return

        rule, created = StudentNumberRule.objects.update_or_create(
            program_type=program_type,
            department=department,
            defaults={
                'admission_year_digits': 3,
                'note': f'dept_code {dept_code} → DB code {db_code} ({dept_name})',
                'is_active': True,
            }
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(
            f'  [{status}] {program_type.name_zh}: '
            f'dept_code={dept_code} → departments.code={db_code} ({dept_name})'
        )
