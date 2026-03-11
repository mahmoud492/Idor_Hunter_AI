"""
crypto_manager.py
────────────────────
نظام التشفير
"""
import os
import base64
try:
    from Crypto.Cipher import AES
    CRYPTO_AVAILABLE = True
except:
    CRYPTO_AVAILABLE = False

class CryptoManager:
    def __init__(self):
        self.key = os.getenv("MASTER_KEY", "default").encode()[:32]
    
    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
