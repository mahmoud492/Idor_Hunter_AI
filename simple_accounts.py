"""
simple_accounts.py
──────────────────
نسخة مبسطة لإدارة الحسابات - بدون مشاكل
"""

import json
from crypto_manager import CryptoManager
from env_loader import EnvLoader

class SimpleAccounts:
    """
    مدير حسابات بسيط - يقرأ accounts.json.enc مباشرة
    """
    
    def __init__(self):
        self.crypto = CryptoManager()
        self.accounts = []
        self._load_accounts()
    
    def _load_accounts(self):
        """تحميل الحسابات من الملف المشفر"""
        try:
            with open('accounts.json.enc', 'r') as f:
                encrypted = f.read()
            
            decrypted = self.crypto.decrypt(encrypted)
            data = json.loads(decrypted)
            self.accounts = data.get('accounts', [])
            print(f"✅ تم تحميل {len(self.accounts)} حسابات")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل الحسابات: {e}")
            self.accounts = []
    
    def get_count(self):
        """عدد الحسابات"""
        return len(self.accounts)
    
    def get_account(self, index=0):
        """الحصول على حساب"""
        if 0 <= index < len(self.accounts):
            return self.accounts[index]
        return None
    
    def get_all(self):
        """كل الحسابات"""
        return self.accounts
    
    def list_accounts(self):
        """عرض الحسابات"""
        print(f"\n📧 الحسابات ({len(self.accounts)}):")
        for i, acc in enumerate(self.accounts, 1):
            print(f"   {i}. {acc['email']}")
    
    def rotate(self):
        """تدوير الحسابات (اختيار التالي)"""
        if not hasattr(self, '_counter'):
            self._counter = 0
        
        if not self.accounts:
            return None
        
        account = self.accounts[self._counter % len(self.accounts)]
        self._counter += 1
        return account


# اختبار سريع
if __name__ == "__main__":
    print("="*60)
    print("📦 SimpleAccounts - اختبار")
    print("="*60)
    
    accounts = SimpleAccounts()
    accounts.list_accounts()
    
    if accounts.get_count() > 0:
        print("\n🔐 اختبار التدوير:")
        for i in range(7):
            acc = accounts.rotate()
            print(f"   {i+1}: {acc['email']}")
    
    print("="*60)
