"""
crypto_manager.py
────────────────────────────────────────────────────────────────────
IDOR Hunter AI - نظام التشفير المركزي
يعمل على: Linux, Windows, Termux, macOS
────────────────────────────────────────────────────────────────────
"""

import os
import json
import base64
from pathlib import Path

# محاولة استيراد cryptography (النسخة العادية)
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ cryptography غير مثبتة. جاري محاولة pycryptodome...")
    
    try:
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        from Crypto.Random import get_random_bytes
        CRYPTO_AVAILABLE = "pycryptodome"
    except ImportError:
        CRYPTO_AVAILABLE = False
        print("❌ لم يتم العثور على أي مكتبة تشفير!")
        print("📦 ثبت واحدة: pip install cryptography أو pip install pycryptodome")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv غير مثبتة. جارٍ التثبيت التلقائي...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True


class CryptoManager:
    """
    مدير التشفير المركزي
    ───────────────────
    - AES-256-GCM (إذا كانت cryptography موجودة)
    - AES-256-CBC (إذا كانت pycryptodome موجودة)
    - يدعم جميع المنصات
    """
    
    def __init__(self, env_path=".env"):
        self.env_path = env_path
        self._master_key = None
        self._load_env()
    
    def _load_env(self):
        """تحميل المتغيرات من .env"""
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path)
            self._master_key = os.getenv("MASTER_KEY")
    
    def set_master_key(self, key: str):
        """تعيين المفتاح الرئيسي"""
        self._master_key = key
        # حفظ في .env
        with open(self.env_path, "w") as f:
            f.write(f'MASTER_KEY="{key}"\n')
    
    def encrypt(self, data: str) -> str:
        """تشفير نص"""
        if not self._master_key:
            raise ValueError("❌ المفتاح الرئيسي غير موجود!")
        
        if CRYPTO_AVAILABLE == True:
            # استخدام cryptography
            key = self._master_key.encode()[:32]
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            encrypted = aesgcm.encrypt(nonce, data.encode(), None)
            combined = nonce + encrypted
            return base64.b64encode(combined).decode()
        
        elif CRYPTO_AVAILABLE == "pycryptodome":
            # استخدام pycryptodome
            key = self._master_key.encode()[:32]
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data.encode())
            combined = cipher.nonce + tag + ciphertext
            return base64.b64encode(combined).decode()
        
        else:
            # تشفير بسيط (للطوارئ)
            print("⚠️ تحذير: استخدام تشفير بسيط غير آمن!")
            encoded = base64.b64encode(data.encode())
            return encoded.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """فك تشفير"""
        if not self._master_key:
            raise ValueError("❌ المفتاح الرئيسي غير موجود!")
        
        if CRYPTO_AVAILABLE == True:
            # استخدام cryptography
            key = self._master_key.encode()[:32]
            combined = base64.b64decode(encrypted_data)
            nonce = combined[:12]
            ciphertext = combined[12:]
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode()
        
        elif CRYPTO_AVAILABLE == "pycryptodome":
            # استخدام pycryptodome
            key = self._master_key.encode()[:32]
            combined = base64.b64decode(encrypted_data)
            nonce = combined[:16]
            tag = combined[16:32]
            ciphertext = combined[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted.decode()
        
        else:
            # فك تشفير بسيط
            decoded = base64.b64decode(encrypted_data).decode()
            return decoded
    
    @staticmethod
    def generate_key() -> str:
        """توليد مفتاح عشوائي"""
        return base64.b64encode(os.urandom(32)).decode()


# اختبار
if __name__ == "__main__":
    print("=" * 60)
    print("🔐 IDOR Hunter - نظام التشفير")
    print("=" * 60)
    
    crypto = CryptoManager()
    
    if not crypto._master_key:
        key = crypto.generate_key()
        crypto.set_master_key(key)
        print(f"✅ تم توليد مفتاح جديد: {key[:10]}...")
    
    test_text = "هذا نص سري للغاية - سر المشروع"
    print(f"\n📝 النص الأصلي: {test_text}")
    
    encrypted = crypto.encrypt(test_text)
    print(f"🔒 النص المشفر: {encrypted[:50]}...")
    
    decrypted = crypto.decrypt(encrypted)
    print(f"🔓 بعد فك التشفير: {decrypted}")
    
    if test_text == decrypted:
        print("\n✅ نظام التشفير يعمل بشكل صحيح!")
    else:
        print("\n❌ خطأ في التشفير!")
    
    print("=" * 60)
