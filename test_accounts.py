# test_accounts.py
import json
from crypto_manager import CryptoManager
from env_loader import EnvLoader

print("="*60)
print("🔍 اختبار قراءة accounts.json.enc مباشرة")
print("="*60)

# 1. قراءة الملف المشفر
try:
    with open('accounts.json.enc', 'r') as f:
        encrypted = f.read()
    print(f"✅ تم قراءة الملف: {len(encrypted)} بايت")
except Exception as e:
    print(f"❌ خطأ في القراءة: {e}")
    exit()

# 2. فك التشفير
try:
    crypto = CryptoManager()
    decrypted = crypto.decrypt(encrypted)
    print("✅ تم فك التشفير بنجاح")
except Exception as e:
    print(f"❌ خطأ في فك التشفير: {e}")
    exit()

# 3. تحويل JSON
try:
    data = json.loads(decrypted)
    print(f"✅ تم تحميل JSON")
    print(f"📊 عدد الحسابات في الملف: {len(data.get('accounts', []))}")
    
    # عرض الحسابات
    accounts = data.get('accounts', [])
    for i, acc in enumerate(accounts, 1):
        print(f"   {i}. {acc['email']}")
except Exception as e:
    print(f"❌ خطأ في JSON: {e}")

print("="*60)
