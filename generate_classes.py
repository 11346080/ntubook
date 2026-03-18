import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from core.models import Department, ClassGroup

def run():
    print("🧹 正在清空舊的班級資料...")
    ClassGroup.objects.all().delete() # ✅ 這行最重要，解決「一堆重複」

    depts = Department.objects.all()
    class_types = ['甲', '乙', '丙']

    new_classes = []
    for dept in depts:
        prog_name = getattr(dept.program_type, 'name_zh', '')
        max_year = 5 if "五專" in prog_name else (2 if any(kw in prog_name for kw in ["二技", "二專", "碩士"]) else 4)
        
        for yr in range(1, max_year + 1):
            for ct in class_types:
                new_classes.append(ClassGroup(
                    department=dept,
                    name_zh=f"{ct}班",
                    code=f"{dept.code}{yr}{ct}",
                    grade=str(yr),
                    class_name=ct
                ))

    ClassGroup.objects.bulk_create(new_classes)
    print(f"✅ 完成！共建立 {len(new_classes)} 個班級。")

if __name__ == "__main__":
    run()