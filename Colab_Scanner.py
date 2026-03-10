"""
colab_scanner.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - Colab Scanner (محدث لقراءة الأهداف من ملف)
────────────────────────────────────────────────────────────────────
"""

import requests
import json
import time
import os
from datetime import datetime
import random

# --------------------------------------------------------------
# الإعدادات
# --------------------------------------------------------------
TARGETS_FILE = "targets.txt"  # ملف الأهداف
RESULTS_DIR = "idor_results"   # مجلد النتائج
DELAY_BETWEEN_REQUESTS = 2      # تأخير بين الطلبات (ثواني)

# --------------------------------------------------------------
# إنشاء المجلدات
# --------------------------------------------------------------
os.makedirs(RESULTS_DIR, exist_ok=True)

# --------------------------------------------------------------
# دوال الفحص
# --------------------------------------------------------------
def load_targets():
    """تحميل قائمة الأهداف من ملف"""
    targets = []
    
    # لو الملف مش موجود، ننشئ ملف افتراضي
    if not os.path.exists(TARGETS_FILE):
        print(f"⚠️ ملف {TARGETS_FILE} غير موجود. إنشاء ملف افتراضي...")
        with open(TARGETS_FILE, 'w') as f:
            f.write("https://example.com\n")
            f.write("https://testphp.vulnweb.com\n")
        print("✅ تم إنشاء ملف الأهداف الافتراضي")
    
    # قراءة الأهداف
    with open(TARGETS_FILE, 'r') as f:
        targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"✅ تم تحميل {len(targets)} هدف")
    return targets

def test_idor(target, param="id", ids=None):
    """
    اختبار IDOR بسيط
    """
    if ids is None:
        ids = [1, 2, 3, 4, 5, 10, 100, 1000, 9999, 12345]
    
    print(f"\n🔍 فحص {target}")
    
    results = []
    
    for id_value in ids:
        try:
            # بناء URL
            if "?" in target:
                url = f"{target}&{param}={id_value}"
            else:
                url = f"{target}?{param}={id_value}"
            
            # إرسال الطلب
            response = requests.get(url, timeout=5)
            
            # تحليل النتيجة
            result = {
                "id": id_value,
                "url": url,
                "status": response.status_code,
                "length": len(response.text),
                "time": datetime.now().isoformat()
            }
            
            print(f"   ID {id_value}: {response.status_code} - {len(response.text)} bytes")
            
            # لو الـ 200 OK لكن المحتوى مختلف
            if response.status_code == 200:
                results.append(result)
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    return results

def save_results(results, target_name):
    """حفظ النتائج في ملف"""
    filename = f"{RESULTS_DIR}/{target_name}_{int(time.time())}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ تم حفظ {len(results)} نتيجة في {filename}")
    return filename

# --------------------------------------------------------------
# الوظيفة الرئيسية
# --------------------------------------------------------------
def main():
    print("="*60)
    print("🚀 IDOR Hunter - Colab Scanner")
    print("="*60)
    print(f"⏰ وقت التشغيل: {datetime.now()}")
    print("="*60)
    
    # تحميل الأهداف
    targets = load_targets()
    
    if not targets:
        print("❌ لا توجد أهداف للفحص!")
        return
    
    total_results = []
    
    # فحص كل هدف
    for target in targets:
        print(f"\n{'─'*60}")
        
        # استخراج اسم الهدف للتسمية
        target_name = target.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        
        # اختبار IDOR
        results = test_idor(target)
        
        if results:
            save_results(results, target_name)
            total_results.extend(results)
        else:
            print(f"⚠️ لا توجد نتائج لـ {target}")
    
    # تقرير نهائي
    print("\n" + "="*60)
    print(f"📊 إجمالي النتائج: {len(total_results)}")
    print("="*60)
    
    # البقاء حياً
    print("\n⏳ الجلسة مستمرة... (اضغط Ctrl+C للإيقاف)")
    try:
        while True:
            time.sleep(60)
            print(f"   ⏱️ {datetime.now()} - لا زلت شغالاً...")
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف التشغيل")

# --------------------------------------------------------------
# التشغيل
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
