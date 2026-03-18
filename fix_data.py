# fix_campus_final.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from core.models import ClassGroup

def run():
    print("🚀 正在根據【班級名稱】反向修正系所校區...")
    
    # 找出所有名稱包含 (桃園) 或 (桃) 的班級
    ty_classes = ClassGroup.objects.filter(name_zh__icontains='桃園') | \
                 ClassGroup.objects.filter(name_zh__icontains='（桃園）')
    
    ty_count = 0
    for cls in ty_classes:
        if cls.department and cls.department.campus != 'TY':
            cls.department.campus = 'TY'
            cls.department.save()
            ty_count += 1

    # 找出所有名稱包含 (臺北) 或 (台北) 的班級
    tp_classes = ClassGroup.objects.filter(name_zh__icontains='臺北') | \
                 ClassGroup.objects.filter(name_zh__icontains='台北')
    
    tp_count = 0
    for cls in tp_classes:
        if cls.department and cls.department.campus != 'TP':
            cls.department.campus = 'TP'
            cls.department.save()
            tp_count += 1
            
    print(f"✅ 修正完成！")
    print(f"已將 {ty_count} 個系所標記為桃園。")
    print(f"已將 {tp_count} 個系所標記為台北。")

if __name__ == "__main__":
    run()