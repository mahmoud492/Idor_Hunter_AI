"""
add_my_accounts.py
────────────────────────────────────────────────────────────────────
IDOR Hunter AI - إضافة حسابات Google الخمسة (مشفر)
⚠️ هذا الملف يحتوي على كلمات سر - لا ترفعه على GitHub
────────────────────────────────────────────────────────────────────
"""

import os
import sys
from pathlib import Path

# إضافة المسار الحالي
sys.path.insert(0, str(Path(__file__).parent))

try:
    from accounts_manager import AccountsManager
    from crypto_manager import CryptoManager
    from env_loader import EnvLoader
    print("✅ تم تحميل المكتبات بنجاح")
except ImportError as e:
    print(f"❌ خطأ: {e}")
    print("تأكد من وجود الملفات: crypto_manager.py, env_loader.py, accounts_manager.py")
    sys.exit(1)


def main():
    """إضافة الحسابات الخمسة"""
    print("="*60)
    print("📧 IDOR Hunter - إضافة حسابات Google")
    print("="*60)
    
    # إنشاء مدير الحسابات
    am = AccountsManager()
    
    # قائمة الحسابات (بريد, كلمة سر)
    accounts = [
        ('gemy28500@gmail.com', 'Idor_Hunter33'),
        ('k77614005@gmail.com', 'Idor_Hunter34'),
        ('Celarens33@gmail.com', 'Idor_Hunter35'),
        ('m39060649@gmail.com', 'Idor_Hunter36'),
        ('mark5794685@gmail.com', 'Idor_Hunter37')
    ]
    
    print("\n📝 جاري إضافة الحسابات...")
    added = 0
    
    for email, password in accounts:
        if am.add_account(email, password, encrypted=True):
            added += 1
            print(f"   ✅ {email}")
    
    # حفظ الحسابات في ملف مشفر
    if added > 0:
        am.save_accounts()
        print(f"\n✅ تم إضافة {added} حسابات وحفظها في accounts.json.enc")
    else:
        print("\n⚠️ لم يتم إضافة أي حسابات (قد تكون موجودة مسبقاً)")
    
    # عرض الإحصائيات
    stats = am.get_statistics()
    print(f"\n📊 الإحصائيات:")
    print(f"   إجمالي الحسابات: {stats['total']}")
    print(f"   نشطة: {stats['active']}")
    
    print("\n" + "="*60)
    print("🔐 جميع كلمات السر مشفرة الآن.")
    print("📁 يمكنك حذف هذا الملف بعد التأكد من نجاح الإضافة.")
    print("="*60)


if __name__ == "__main__":
    main()
