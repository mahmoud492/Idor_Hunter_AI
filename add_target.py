"""
add_target.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - إضافة أهداف جديدة
────────────────────────────────────────────────────────────────────
"""

import os
from datetime import datetime

TARGETS_FILE = "targets.txt"

def show_current_targets():
    """عرض الأهداف الحالية"""
    if not os.path.exists(TARGETS_FILE):
        print("📂 لا توجد أهداف حالياً")
        return []
    
    with open(TARGETS_FILE, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]
    
    if targets:
        print(f"\n📋 الأهداف الحالية ({len(targets)}):")
        for i, target in enumerate(targets, 1):
            print(f"   {i}. {target}")
    else:
        print("📂 لا توجد أهداف حالياً")
    
    return targets

def add_target(new_target):
    """إضافة هدف جديد"""
    targets = []
    
    # قراءة الأهداف الموجودة
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    
    # التحقق من عدم التكرار
    if new_target in targets:
        print(f"⚠️ الهدف {new_target} موجود بالفعل!")
        return False
    
    # إضافة الهدف
    targets.append(new_target)
    
    # حفظ الملف
    with open(TARGETS_FILE, 'w') as f:
        for target in targets:
            f.write(target + "\n")
    
    print(f"✅ تم إضافة: {new_target}")
    return True

def remove_target(index):
    """حذف هدف"""
    if not os.path.exists(TARGETS_FILE):
        print("❌ لا توجد أهداف")
        return False
    
    with open(TARGETS_FILE, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]
    
    if 1 <= index <= len(targets):
        removed = targets.pop(index-1)
        
        with open(TARGETS_FILE, 'w') as f:
            for target in targets:
                f.write(target + "\n")
        
        print(f"✅ تم حذف: {removed}")
        return True
    else:
        print("❌ رقم غير صحيح")
        return False

def clear_all_targets():
    """مسح كل الأهداف"""
    sure = input("⚠️ هل أنت متأكد؟ (yes/no): ")
    if sure.lower() == 'yes':
        open(TARGETS_FILE, 'w').close()
        print("✅ تم مسح كل الأهداف")
        return True
    return False

def main():
    """القائمة الرئيسية"""
    while True:
        print("\n" + "="*60)
        print("🎯 IDOR Hunter - إدارة الأهداف")
        print("="*60)
        print("1. عرض الأهداف")
        print("2. إضافة هدف")
        print("3. حذف هدف")
        print("4. مسح الكل")
        print("5. خروج")
        print("="*60)
        
        choice = input("اختيارك: ").strip()
        
        if choice == '1':
            show_current_targets()
        
        elif choice == '2':
            new_target = input("أدخل الهدف (مثال: https://example.com): ").strip()
            if new_target:
                add_target(new_target)
            else:
                print("❌ لم تدخل شيء")
        
        elif choice == '3':
            targets = show_current_targets()
            if targets:
                try:
                    idx = int(input("رقم الهدف للحذف: "))
                    remove_target(idx)
                except:
                    print("❌ رقم غير صحيح")
        
        elif choice == '4':
            clear_all_targets()
        
        elif choice == '5':
            print("👋 السلام عليكم")
            break
        
        else:
            print("❌ اختيار غير صحيح")

if __name__ == "__main__":
    main()
