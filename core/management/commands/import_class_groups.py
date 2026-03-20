"""
Management command: python manage.py import_class_groups
Idempotent: safe to re-run. Updates existing records, creates new ones.
"""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ntub_usedbooks.settings import BASE_DIR
from core.models import Campus, ProgramType, Department, ClassGroup


# Campus determination: shared depts get TWO records (TP + TY).
# Regular depts: default to TP (confirmed by JSON campus text where available).
_SHARED_DEPT_VALS = {'400', '300', '500', '901', '902', '903'}
_TP_DEFAULT_DEPT_VALS = {
    '401', '402', '403', '404', '405', '406', '407',
    '40A', '40B', '40C',
    '301', '302', '303', '304', '305', '306', '307', '30A', '30B',
    '503', '504', '505', '506', '508', '509', '521',
}


def _parse_campus_from_text(cls_text: str) -> str | None:
    """Return 'TP', 'TY', or None based on cls_text content."""
    if '(桃園)' in cls_text:
        return 'TY'
    if '(臺北)' in cls_text:
        return 'TP'
    return None


def _extract_grade_no(cls_val: str, dept_val: str, cls_text: str) -> int | None:
    """
    Extract grade_no from cls_val.
    - Regular depts: cls_val[3] is a digit → grade = int(cls_val[3])
    - Shared depts (400/300/500/901/902/903): cls_val[3] is NOT the student grade,
      it's a course-type/level code.
      Return None for now (needs manual confirmation).
    """
    if dept_val in _SHARED_DEPT_VALS:
        return None
    # Regular dept: cls_val format is 6 chars, dept_val is 3 chars.
    # suffix = cls_val[3:6], e.g. "10A", "20B"
    if len(cls_val) >= 4:
        ch = cls_val[3]
        if ch.isdigit():
            return int(ch)
    return None


def _extract_section_code(cls_val: str) -> str:
    """Extract section code from last char of cls_val."""
    return cls_val[-1] if cls_val else ''


class Command(BaseCommand):
    help = 'Import class group data from ntub_all_classes.json (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-path',
            type=str,
            default=None,
            help='Path to ntub_all_classes.json (defaults to project root)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )

    def handle(self, *args, **options):
        json_path = options['json_path']
        if not json_path:
            json_path = os.path.join(BASE_DIR, '..', 'ntub_all_classes.json')
        json_path = os.path.abspath(json_path)

        if not os.path.exists(json_path):
            raise CommandError(f'JSON file not found: {json_path}')

        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        if not raw_data:
            raise CommandError('JSON file is empty')

        self.stdout.write(f'Loaded {len(raw_data)} records from {json_path}')

        # Pre-build ProgramType lookup: edu_val → ProgramType
        program_type_map = {}
        for item in raw_data:
            ev = item['edu_val']
            if ev not in program_type_map:
                program_type_map[ev] = None  # placeholder

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('[DRY RUN]'))
            self.stdout.write(f'  Would process {len(raw_data)} records')
            self.stdout.write(f'  Unique edu_vals: {sorted(program_type_map.keys())}')
            return

        with transaction.atomic():
            self._import(program_type_map, raw_data)

        self._report()

    def _import(self, program_type_map, raw_data):
        # ── 1. Campuses ──────────────────────────────────────────────────────
        tp, _ = Campus.objects.update_or_create(
            code='TP',
            defaults={'name_zh': '臺北校區', 'short_name': '臺北', 'sort_order': 1},
        )
        ty, _ = Campus.objects.update_or_create(
            code='TY',
            defaults={'name_zh': '桃園校區', 'short_name': '桃園', 'sort_order': 2},
        )
        campus_map = {'TP': tp, 'TY': ty}
        self.stdout.write(f'  Campuses: TP={tp.pk}, TY={ty.pk}')

        # ── 2. ProgramTypes ─────────────────────────────────────────────────
        # edu_val → code, edu_text → name_zh
        edu_meta = {}  # edu_val → (code, name_zh)
        for item in raw_data:
            ev = item['edu_val']
            if ev not in edu_meta:
                edu_meta[ev] = (ev, item['edu_text'])

        for ev, (code, name_zh) in edu_meta.items():
            pt, created = ProgramType.objects.update_or_create(
                code=code,
                defaults={'name_zh': name_zh, 'sort_order': 10 if not created else 99},
            )
            program_type_map[ev] = pt
            status = 'created' if created else 'updated'
            self.stdout.write(f'    ProgramType {status}: {ev} = {name_zh}')

        # ── 3. Departments ─────────────────────────────────────────────────
        # Collect all (dept_val, edu_val) combinations
        dept_keys = {}  # (dept_val, ev) → (dept_text, cls_texts)
        for item in raw_data:
            key = (item['dept_val'], item['edu_val'])
            if key not in dept_keys:
                dept_keys[key] = {'dept_text': item['dept_text'], 'cls_texts': []}
            dept_keys[key]['cls_texts'].append(item['cls_text'])

        # Also track which campuses shared depts need
        shared_campus_map = {}  # (dept_val, ev) → set of {'TP', 'TY'}

        for item in raw_data:
            campus_from_text = _parse_campus_from_text(item['cls_text'])
            if campus_from_text and item['dept_val'] in _SHARED_DEPT_VALS:
                key = (item['dept_val'], item['edu_val'])
                shared_campus_map.setdefault(key, set()).add(campus_from_text)

        # For shared depts that only appear in one campus in JSON,
        # add the other campus as well to make it complete.
        for (dv, ev), camps in list(shared_campus_map.items()):
            if len(camps) == 1:
                other = 'TY' if 'TP' in camps else 'TP'
                camps.add(other)
                shared_campus_map[(dv, ev)] = camps

        dept_objects = {}  # (dept_val, ev, campus_code) → Department instance

        for (dept_val, ev), meta in dept_keys.items():
            pt = program_type_map.get(ev)
            if not pt:
                self.stdout.write(
                    self.style.WARNING(f'    Skipping dept {dept_val} (ev={ev}): no ProgramType')
                )
                continue

            is_shared = dept_val in _SHARED_DEPT_VALS

            if is_shared:
                # Create one record per campus
                camps_needed = shared_campus_map.get((dept_val, ev), {'TP', 'TY'})
                for c_code in sorted(camps_needed):
                    campus = campus_map.get(c_code)
                    if not campus:
                        continue
                    dept, created = Department.objects.update_or_create(
                        campus=campus,
                        program_type=pt,
                        code=dept_val,
                        defaults={'name_zh': meta['dept_text']},
                    )
                    dept_objects[(dept_val, ev, c_code)] = dept
                    status = 'created' if created else 'updated'
                    self.stdout.write(f'    Dept {status}: {dept_val} / {ev} / {c_code} = {meta["dept_text"]}')
            else:
                # Regular dept: default to TP
                campus = campus_map['TP']
                dept, created = Department.objects.update_or_create(
                    campus=campus,
                    program_type=pt,
                    code=dept_val,
                    defaults={'name_zh': meta['dept_text']},
                )
                dept_objects[(dept_val, ev, 'TP')] = dept
                status = 'created' if created else 'updated'
                self.stdout.write(f'    Dept {status}: {dept_val} / {ev} / TP = {meta["dept_text"]}')

        # ── 4. ClassGroups ─────────────────────────────────────────────────
        # Build cls_val → dept object lookup
        # Key by (dept_val, ev) for shared depts: need campus context
        cls_dept_lookup = {}  # cls_val → Department instance

        for item in raw_data:
            dv = item['dept_val']
            ev = item['edu_val']
            cv = item['cls_val']

            if dv in _SHARED_DEPT_VALS:
                # Find campus from cls_text
                c_code = _parse_campus_from_text(item['cls_text']) or 'TP'
                key = (dv, ev, c_code)
            else:
                key = (dv, ev, 'TP')

            dept_obj = dept_objects.get(key)
            if dept_obj:
                cls_dept_lookup[cv] = dept_obj
            else:
                self.stdout.write(
                    self.style.WARNING(f'    No dept for cls_val={cv}, dv={dv}, ev={ev}')
                )

        imported_groups = []
        skipped_grade = []

        for item in raw_data:
            cv = item['cls_val']
            dv = item['dept_val']
            ev = item['edu_val']

            dept_obj = cls_dept_lookup.get(cv)
            if not dept_obj:
                continue

            grade_no = _extract_grade_no(cv, dv, item['cls_text'])
            section_code = _extract_section_code(cv)

            if grade_no is None:
                skipped_grade.append(cv)
                grade_no = 1  # temporary placeholder, mark for review

            cg, created = ClassGroup.objects.update_or_create(
                code=cv,
                defaults={
                    'department': dept_obj,
                    'name_zh': item['cls_text'],
                    'grade_no': grade_no,
                    'section_code': section_code,
                },
            )
            imported_groups.append((cv, created, grade_no is None))

        self.stdout.write(f'\n  ClassGroups: {len(imported_groups)} total')
        self.stdout.write(f'  ClassGroups created: {sum(1 for _, c, _ in imported_groups if c)}')
        self.stdout.write(f'  ClassGroups updated: {sum(1 for _, c, _ in imported_groups if not c)}')

        if skipped_grade:
            self.stdout.write(
                self.style.WARNING(
                    f'\n  WARNING: {len(skipped_grade)} shared-dept records have NULL grade_no '
                    f'(expected for shared courses like 通識/體育/軍訓):\n    '
                    + ', '.join(sorted(skipped_grade))
                )
            )
            self.stdout.write(
                '    These need manual confirmation of correct grade_no values.\n'
                '    Shared-dept grade_no should be set to NULL or specific course-level codes.'
            )

    def _report(self):
        self.stdout.write('\n=== Import Summary ===')
        self.stdout.write(f'  Campuses:      {Campus.objects.count()}')
        self.stdout.write(f'  ProgramTypes:  {ProgramType.objects.count()}')
        self.stdout.write(f'  Departments:   {Department.objects.count()}')
        self.stdout.write(f'  ClassGroups:   {ClassGroup.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nImport completed successfully.'))
