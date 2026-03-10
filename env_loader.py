"""
env_loader.py
────────────────────────────────────────────────────────────────────
IDOR Hunter AI - إدارة المتغيرات البيئية والملفات السرية
────────────────────────────────────────────────────────────────────
"""

import os
import sys
import stat
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv غير مثبت. جاري التثبيت...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True


class EnvLoader:
    """
    محمل البيئة الآمن
    ─────────────────
    - إدارة ملفات .env
    - التحقق من الصلاحيات
    - تحميل المتغيرات
    - دعم التشفير
    """
    
    def __init__(self, env_path: str = ".env"):
        """
        تهيئة محمل البيئة
        ─────────────────
        env_path: مسار ملف .env (افتراضي: ".env")
        """
        self.env_path = Path(env_path)
        self._check_permissions()
        self._load_env_file()
        self._vars: Dict[str, str] = {}
    
    def _check_permissions(self):
        """
        التحقق من صلاحيات الملف
        ───────────────────────
        - يتأكد أن الملف للقراءة فقط
        - يمنع وصول الآخرين
        """
        if not self.env_path.exists():
            # إنشاء ملف جديد بصلاحيات آمنة
            self.env_path.touch()
            os.chmod(self.env_path, 0o600)  # rw------- (فقط للمالك)
            print(f"✅ تم إنشاء {self.env_path}")
            return
        
        # التحقق من الصلاحيات الحالية
        current_perms = stat.S_IMODE(os.stat(self.env_path).st_mode)
        
        # إذا كان الملف قابلاً للقراءة من الآخرين
        if current_perms & 0o077:  # 0o077 = أي صلاحية للـ group/others
            print(f"⚠️ تحذير: {self.env_path} له صلاحيات خطيرة!")
            print("🔧 جاري التصحيح...")
            os.chmod(self.env_path, 0o600)
            print("✅ تم تعديل الصلاحيات إلى 600 (آمن)")
    
    def _load_env_file(self):
        """تحميل المتغيرات من ملف .env"""
        if self.env_path.exists() and DOTENV_AVAILABLE:
            load_dotenv(self.env_path)
            print(f"✅ تم تحميل {self.env_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        الحصول على متغير بيئة
        ─────────────────────
        key: اسم المتغير
        default: القيمة الافتراضية إذا لم يوجد
        """
        value = os.getenv(key, default)
        
        # تخزين في الذاكرة للوصول السريع
        if value is not None:
            self._vars[key] = str(value)
        
        return value
    
    def get_required(self, key: str) -> str:
        """
        الحصول على متطلبات إلزامية
        ──────────────────────────
        key: اسم المتغير
        يرفع خطأ إذا لم يوجد
        """
        value = self.get(key)
        if value is None:
            error_msg = f"❌ المتغير {key} مطلوب في ملف {self.env_path}"
            print(error_msg)
            print(f"💡 أضف السطر: {key}=your_value_here")
            raise ValueError(error_msg)
        return value
    
    def set(self, key: str, value: str, encrypt: bool = False):
        """
        تعيين متغير بيئة وحفظه في الملف
        ──────────────────────────────
        key: اسم المتغير
        value: القيمة
        encrypt: هل يتم التشفير؟ (يحتاج CryptoManager)
        """
        if encrypt:
            try:
                from crypto_manager import CryptoManager
                crypto = CryptoManager()
                value = crypto.encrypt(value)
            except ImportError:
                print("⚠️ تحذير: crypto_manager غير موجود. التخزين بدون تشفير.")
        
        # تحديث في الذاكرة
        os.environ[key] = value
        self._vars[key] = value
        
        # تحديث في الملف
        lines = []
        updated = False
        
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        with open(self.env_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.startswith(f"{key}="):
                    f.write(f'{key}="{value}"\n')
                    updated = True
                else:
                    f.write(line)
            
            if not updated:
                f.write(f'{key}="{value}"\n')
        
        # تأمين الملف
        os.chmod(self.env_path, 0o600)
        print(f"✅ تم حفظ {key} في {self.env_path}")
    
    def get_all(self) -> Dict[str, str]:
        """الحصول على جميع المتغيرات"""
        return dict(self._vars)
    
    def delete(self, key: str):
        """حذف متغير"""
        if key in os.environ:
            del os.environ[key]
        
        if key in self._vars:
            del self._vars[key]
        
        # تحديث الملف
        if self.env_path.exists():
            lines = []
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(self.env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if not line.startswith(f"{key}="):
                        f.write(line)
            
            print(f"✅ تم حذف {key} من {self.env_path}")
    
    def create_default_env(self, master_key: str = None):
        """
        إنشاء ملف .env افتراضي
        ─────────────────────
        master_key: المفتاح الرئيسي (اختياري)
        """
        if not master_key:
            # توليد مفتاح عشوائي
            try:
                from crypto_manager import CryptoManager
                master_key = CryptoManager.generate_key()
            except ImportError:
                import secrets
                master_key = secrets.token_urlsafe(32)
        
        content = f"""# المفتاح الرئيسي للمشروع - احفظه في مكان آمن
# تم الإنشاء: {__import__('datetime').datetime.now()}
MASTER_KEY="{master_key}"

# مفاتيح APIs (ستضاف لاحقاً)
TWITTER_API_KEY=""
GITHUB_API_KEY=""
REDDIT_API_KEY=""
HACKERONE_API_KEY=""
BUGCROWD_API_KEY=""

# إعدادات عامة
MAX_WORKERS=50
REQUEST_TIMEOUT=30
USER_AGENT="IDOR-Hunter/1.0"

# إعدادات Google
GOOGLE_ACCOUNTS_COUNT=50
GOOGLE_DRIVE_BASE_FOLDER="IDOR_Hunter_Data"

# إعدادات متقدمة
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_ENCRYPTION=true
"""
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.chmod(self.env_path, 0o600)
        print(f"✅ تم إنشاء {self.env_path}")
        print(f"🔑 المفتاح الرئيسي: {master_key[:10]}...")
        print("⚠️ احفظ هذا المفتاح في مكان آمن!")
        
        return master_key
    
    def validate_required_keys(self, required_keys: List[str]) -> bool:
        """
        التحقق من وجود مفاتيح مطلوبة
        ────────────────────────────
        required_keys: قائمة المفاتيح المطلوبة
        """
        missing = []
        for key in required_keys:
            if not self.get(key):
                missing.append(key)
        
        if missing:
            print("❌ المفاتيح التالية غير موجودة:")
            for key in missing:
                print(f"   - {key}")
            return False
        
        print("✅ جميع المفاتيح المطلوبة موجودة")
        return True
    
    def export_to_json(self, json_path: str = "env_backup.json"):
        """تصدير المتغيرات لملف JSON"""
        import json
        data = {
            "variables": self.get_all(),
            "exported_at": str(__import__('datetime').datetime.now())
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ تم التصدير إلى {json_path}")
        return json_path


# اختبار
if __name__ == "__main__":
    print("=" * 60)
    print("🔐 IDOR Hunter - إدارة البيئة")
    print("=" * 60)
    
    # تهيئة
    env = EnvLoader()
    
    # إنشاء ملف افتراضي إذا لم يكن موجوداً
    if not env.get("MASTER_KEY"):
        print("📝 إنشاء ملف .env افتراضي...")
        master_key = env.create_default_env()
    
    # اختبار المتغيرات
    print("\n📊 المتغيرات الحالية:")
    for key, value in env.get_all().items():
        print(f"   {key}: {value[:20]}..." if len(str(value)) > 20 else f"   {key}: {value}")
    
    # اختبار حفظ متغير جديد
    print("\n📝 اختبار حفظ متغير...")
    env.set("TEST_VAR", "هذه قيمة اختبار")
    
    # استرجاع المتغير
    test_var = env.get("TEST_VAR")
    print(f"   TEST_VAR = {test_var}")
    
    print("=" * 60)
    print("✅ نظام البيئة يعمل بشكل صحيح!")
    print("=" * 60)
