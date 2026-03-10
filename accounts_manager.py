"""
accounts_manager.py
────────────────────────────────────────────────────────────────────
IDOR Hunter AI - إدارة حسابات Google (5 حسابات حالياً)
────────────────────────────────────────────────────────────────────
"""

import os
import json
import time
import base64
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

try:
    from crypto_manager import CryptoManager
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ crypto_manager غير موجود. سيتم استخدام تخزين غير مشفر!")

try:
    from env_loader import EnvLoader
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False
    print("⚠️ env_loader غير موجود. سيتم استخدام الإعدادات الافتراضية.")


class AccountsManager:
    """
    مدير حسابات Google
    ─────────────────
    - يدعم 5 حسابات حالياً (قابل للتوسع)
    - تخزين آمن مع تشفير
    - تدوير الحسابات تلقائياً
    - مراقبة الاستخدام
    """
    
    def __init__(self, accounts_file: str = "accounts.json.enc"):
        self.accounts_file = Path(accounts_file)
        self.accounts: List[Dict] = []
        self.usage_log: Dict[str, List[datetime]] = {}
        self.current_index = 0
        self.last_rotation = datetime.now()
        
        # تحميل crypto manager
        if CRYPTO_AVAILABLE:
            self.crypto = CryptoManager()
        else:
            self.crypto = None
        
        # تحميل env loader
        if ENV_AVAILABLE:
            self.env = EnvLoader()
        else:
            self.env = None
        
        # تحميل الحسابات
        self._load_accounts()
        
        # إذا مفيش حسابات، نحط الـ 5 حسابات
        if len(self.accounts) == 0:
            self._init_default_accounts()
    
    def _load_accounts(self):
        """تحميل الحسابات من الملف المشفر"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, 'rb') as f:
                    encrypted_data = f.read()
                
                if self.crypto and encrypted_data:
                    # فك التشفير (هينزل في التحديث الجاي)
                    pass
                else:
                    # قراءة عادية (مؤقتاً)
                    pass
            except Exception as e:
                print(f"⚠️ خطأ في تحميل الحسابات: {e}")
    
    def _init_default_accounts(self):
        """
        تهيئة الحسابات الافتراضية (الـ 5 حسابات بتاعتك)
        ─────────────────────────────────────────────
        هتضيفهم يدوياً من خلال الدالة add_account
        """
        print("\n" + "="*60)
        print("📧 IDOR Hunter - إدارة حسابات Google")
        print("="*60)
        print("\n⚠️ لم يتم العثور على حسابات محفوظة.")
        print("📝 يرجى إضافة حساباتك باستخدام الدوال التالية:\n")
        print("   from accounts_manager import AccountsManager")
        print("   am = AccountsManager()")
        print("   am.add_account('email@gmail.com', 'password')")
        print("   am.save_accounts()\n")
        print("="*60)
    
    def add_account(self, email: str, password: str, encrypted: bool = True):
        """
        إضافة حساب جديد
        ──────────────
        email: البريد الإلكتروني
        password: كلمة المرور
        encrypted: هل يتم التشفير؟
        """
        # التحقق من عدم التكرار
        for acc in self.accounts:
            if acc['email'] == email:
                print(f"⚠️ الحساب {email} موجود بالفعل!")
                return False
        
        # تشفير كلمة المرور إذا لزم
        if encrypted and self.crypto:
            encrypted_pass = self.crypto.encrypt(password)
        else:
            encrypted_pass = password
        
        # إضافة الحساب
        account = {
            'email': email,
            'password': encrypted_pass,
            'encrypted': encrypted,
            'added': datetime.now().isoformat(),
            'last_used': None,
            'use_count': 0,
            'status': 'active',
            'notes': ''
        }
        
        self.accounts.append(account)
        print(f"✅ تم إضافة {email}")
        return True
    
    def add_accounts_bulk(self, accounts_list: List[Tuple[str, str]]):
        """
        إضافة عدة حسابات دفعة واحدة
        ──────────────────────────
        accounts_list: قائمة من (البريد, كلمة المرور)
        """
        added = 0
        for email, password in accounts_list:
            if self.add_account(email, password, encrypted=True):
                added += 1
        
        print(f"\n✅ تم إضافة {added} حسابات بنجاح")
        return added
    
    def save_accounts(self):
        """حفظ الحسابات في ملف مشفر"""
        if not self.accounts:
            print("⚠️ لا توجد حسابات للحفظ")
            return False
        
        # تحضير البيانات للحفظ
        data = {
            'accounts': self.accounts,
            'total': len(self.accounts),
            'last_saved': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        try:
            if self.crypto:
                # تشفير البيانات
                encrypted = self.crypto.encrypt(json.dumps(data, ensure_ascii=False))
                with open(self.accounts_file, 'w', encoding='utf-8') as f:
                    f.write(encrypted)
            else:
                # حفظ بدون تشفير (مؤقت)
                json_path = self.accounts_file.with_suffix('.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"⚠️ تم الحفظ بدون تشفير في {json_path}")
            
            print(f"✅ تم حفظ {len(self.accounts)} حسابات")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
            return False
    
    def get_account(self, index: Optional[int] = None) -> Optional[Dict]:
        """
        الحصول على حساب
        ───────────────
        index: رقم الحساب (إذا لم يعطى، يتم التدوير)
        """
        if not self.accounts:
            print("⚠️ لا توجد حسابات متاحة!")
            return None
        
        if index is not None:
            if 0 <= index < len(self.accounts):
                account = self.accounts[index].copy()
            else:
                print(f"⚠️ الحساب رقم {index} غير موجود")
                return None
        else:
            # تدوير الحسابات
            account = self._rotate_account()
            if not account:
                return None
        
        # تحديث سجل الاستخدام
        email = account['email']
        if email not in self.usage_log:
            self.usage_log[email] = []
        
        self.usage_log[email].append(datetime.now())
        
        # تحديث في القائمة الأصلية
        for acc in self.accounts:
            if acc['email'] == email:
                acc['last_used'] = datetime.now().isoformat()
                acc['use_count'] = acc.get('use_count', 0) + 1
                break
        
        # فك تشفير كلمة المرور إذا لزم
        if account.get('encrypted') and self.crypto:
            try:
                account['password'] = self.crypto.decrypt(account['password'])
            except:
                print(f"⚠️ فشل فك تشفير كلمة المرور لـ {email}")
        
        return account
    
    def _rotate_account(self) -> Optional[Dict]:
        """
        تدوير الحسابات (اختيار الأقل استخداماً)
        ───────────────────────────────────────
        """
        if not self.accounts:
            return None
        
        # حساب مرات الاستخدام
        now = datetime.now()
        available = []
        
        for acc in self.accounts:
            email = acc['email']
            if acc.get('status') != 'active':
                continue
            
            # حساب عدد الاستخدامات في آخر ساعة
            recent_uses = 0
            if email in self.usage_log:
                recent_uses = sum(1 for dt in self.usage_log[email] 
                                if now - dt < timedelta(hours=1))
            
            available.append((acc, recent_uses))
        
        if not available:
            print("⚠️ لا توجد حسابات نشطة!")
            return None
        
        # اختيار الحساب الأقل استخداماً
        available.sort(key=lambda x: x[1])
        return available[0][0].copy()
    
    def get_accounts_count(self) -> int:
        """عدد الحسابات"""
        return len(self.accounts)
    
    def get_active_count(self) -> int:
        """عدد الحسابات النشطة"""
        return sum(1 for acc in self.accounts if acc.get('status') == 'active')
    
    def list_accounts(self, show_usage: bool = True):
        """
        عرض قائمة الحسابات
        ──────────────────
        show_usage: عرض إحصائيات الاستخدام
        """
        print("\n" + "="*60)
        print(f"📊 قائمة الحسابات ({len(self.accounts)} حساب)")
        print("="*60)
        
        for i, acc in enumerate(self.accounts):
            status = "✅" if acc.get('status') == 'active' else "❌"
            print(f"\n{status} [{i}] {acc['email']}")
            
            if show_usage:
                last = acc.get('last_used', 'لم يستخدم بعد')
                if last and last != 'لم يستخدم بعد':
                    last = last[:19]  # اختصار
                print(f"   📅 آخر استخدام: {last}")
                print(f"   🔢 عدد الاستخدامات: {acc.get('use_count', 0)}")
        
        print("\n" + "="*60)
    
    def remove_account(self, email_or_index):
        """حذف حساب"""
        if isinstance(email_or_index, int):
            index = email_or_index
            if 0 <= index < len(self.accounts):
                email = self.accounts[index]['email']
                del self.accounts[index]
                print(f"✅ تم حذف {email}")
                return True
        else:
            email = email_or_index
            for i, acc in enumerate(self.accounts):
                if acc['email'] == email:
                    del self.accounts[i]
                    print(f"✅ تم حذف {email}")
                    return True
        
        print(f"⚠️ الحساب غير موجود")
        return False
    
    def update_account_status(self, email: str, status: str):
        """تحديث حالة حساب"""
        for acc in self.accounts:
            if acc['email'] == email:
                acc['status'] = status
                print(f"✅ تم تحديث حالة {email} إلى {status}")
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """إحصائيات الحسابات"""
        stats = {
            'total': len(self.accounts),
            'active': self.get_active_count(),
            'total_uses': sum(acc.get('use_count', 0) for acc in self.accounts),
            'by_status': {},
            'by_usage': {}
        }
        
        # إحصائيات حسب الحالة
        for acc in self.accounts:
            status = acc.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return stats


# اختبار سريع
if __name__ == "__main__":
    print("="*60)
    print("📧 IDOR Hunter - إدارة حسابات Google")
    print("="*60)
    
    # تهيئة المدير
    am = AccountsManager()
    
    # لو عايز تضيف حساباتك دلوقتي
    print("\n📝 لإضافة حساباتك، استخدم:")
    print("    am.add_account('email@gmail.com', 'password')")
    print("    am.save_accounts()")
    
    # مثال (علقها لو مش عايز تستخدمها)
    """
    # إضافة الـ 5 حسابات
    accounts = [
        ('gemy28500@gmail.com', 'كلمة_السر_هنا'),
        ('k77614005@gmail.com', 'كلمة_السر_هنا'),
        ('Celarens33@gmail.com', 'كلمة_السر_هنا'),
        ('m39060649@gmail.com', 'كلمة_السر_هنا'),
        ('mark5794685@gmail.com', 'كلمة_السر_هنا')
    ]
    
    for email, pwd in accounts:
        am.add_account(email, pwd)
    
    am.save_accounts()
    """
    
    print("\n" + "="*60)
