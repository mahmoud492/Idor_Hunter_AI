"""
drive_manager.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - Google Drive Manager (معدل للعمل مع أي redirect URI)
────────────────────────────────────────────────────────────────────
"""

import os
import pickle
import json
import socket
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Google Drive API
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

from simple_accounts import SimpleAccounts

class DriveManager:
    """
    مدير Google Drive - رفع وتنزيل الملفات
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, account_index: int = 0):
        self.account_index = account_index
        self.accounts = SimpleAccounts()
        self.service = None
        self.creds = None
        self.token_file = Path(f"credentials/token_{account_index}.pickle")
        
        if not GOOGLE_AVAILABLE:
            print("❌ Google API libraries not available")
            return
        
        self._authenticate()
    
    def _authenticate(self):
        """
        تسجيل الدخول إلى Google Drive
        """
        account = self.accounts.get_account(self.account_index)
        if not account:
            print(f"❌ Account {self.account_index} not found")
            return
        
        print(f"🔐 Authenticating {account['email']}...")
        
        # تحميل التوكن المخزن
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                print("✅ Loaded existing token")
            except:
                pass
        
        # إذا التوكن منتهي أو غير موجود
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    print("✅ Token refreshed")
                except:
                    self.creds = None
            
            if not self.creds:
                # أول مرة - نحتاج تسجيل دخول
                creds_file = Path("credentials/credentials.json")
                if not creds_file.exists():
                    print(f"❌ credentials.json not found for account {self.account_index}")
                    print("Please download from Google Cloud Console and save to credentials/credentials.json")
                    return
                
                try:
                    # استخدام طريقة manual
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(creds_file), self.SCOPES)
                    
                    # تعديل redirect_uris ليشمل كل الاحتمالات
                    flow.redirect_uri = 'http://localhost:8080/'
                    
                    print("\n" + "="*60)
                    print("🔑 GOOGLE AUTHENTICATION REQUIRED")
                    print("="*60)
                    print("\n1. Open this URL in your browser:")
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(auth_url)
                    print("\n2. Sign in with your Google account")
                    print("3. After granting permission, you'll be redirected to a page")
                    print("4. Copy the FULL URL of that page and paste it here\n")
                    
                    # محاولة فتح الرابط تلقائياً (اختياري)
                    try:
                        webbrowser.open(auth_url)
                        print("🌐 Browser opened automatically")
                    except:
                        pass
                    
                    redirected_url = input("Paste the full redirect URL here: ").strip()
                    
                    # استخراج code من URL
                    from urllib.parse import urlparse, parse_qs
                    parsed_url = urlparse(redirected_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    if 'code' in query_params:
                        code = query_params['code'][0]
                        flow.fetch_token(code=code)
                        self.creds = flow.credentials
                        print("✅ Authentication successful")
                    else:
                        print("❌ No code found in the URL")
                        return
                    
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
                    return
            
            # حفظ التوكن
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            print(f"✅ Token saved to {self.token_file}")
        
        # بناء service
        self.service = build('drive', 'v3', credentials=self.creds)
        print(f"✅ Connected to Google Drive as {account['email']}")
    
    def list_files(self, folder_id: str = 'root') -> List[Dict]:
        """
        عرض الملفات في مجلد
        """
        if not self.service:
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            print(f"📂 Found {len(files)} files")
            return files
        except HttpError as e:
            print(f"❌ Error listing files: {e}")
            return []
    
    def upload_file(self, local_path: str, folder_id: str = 'root', name: Optional[str] = None) -> Optional[str]:
        """
        رفع ملف إلى Drive
        """
        if not self.service:
            return None
        
        if not os.path.exists(local_path):
            print(f"❌ File not found: {local_path}")
            return None
        
        file_name = name or os.path.basename(local_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(local_path, resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            print(f"✅ Uploaded {file_name} to Drive (ID: {file_id})")
            return file_id
        except HttpError as e:
            print(f"❌ Upload failed: {e}")
            return None
    
    def download_file(self, file_id: str, local_path: str) -> bool:
        """
        تحميل ملف من Drive
        """
        if not self.service:
            return False
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"📥 Download {int(status.progress() * 100)}%")
            
            print(f"✅ Downloaded to {local_path}")
            return True
        except HttpError as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def create_folder(self, folder_name: str, parent_id: str = 'root') -> Optional[str]:
        """
        إنشاء مجلد جديد
        """
        if not self.service:
            return None
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            print(f"✅ Created folder '{folder_name}' (ID: {folder_id})")
            return folder_id
        except HttpError as e:
            print(f"❌ Failed to create folder: {e}")
            return None
    
    def search_files(self, query: str) -> List[Dict]:
        """
        البحث عن ملفات
        """
        if not self.service:
            return []
        
        try:
            results = self.service.files().list(
                q=f"name contains '{query}' and trashed=false",
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            print(f"🔍 Found {len(files)} files matching '{query}'")
            return files
        except HttpError as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """
        حذف ملف
        """
        if not self.service:
            return False
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ Deleted file {file_id}")
            return True
        except HttpError as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        الحصول على معلومات ملف
        """
        if not self.service:
            return None
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, owners"
            ).execute()
            return file
        except HttpError as e:
            print(f"❌ Failed to get file info: {e}")
            return None
    
    def save_results(self, results: Dict, filename: str = "drive_results.json"):
        """
        حفظ النتائج
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Results saved to {filename}")
        return filename


# اختبار
if __name__ == "__main__":
    print("="*60)
    print("📁 Google Drive Manager - IDOR Hunter")
    print("="*60)
    
    # اختبار لأول حساب
    drive = DriveManager(account_index=0)
    
    if drive.service:
        # عرض الملفات في root
        files = drive.list_files()
        for f in files[:5]:  # أول 5 ملفات
            print(f"  📄 {f['name']} ({f.get('size', 'N/A')} bytes)")
        
        # إنشاء مجلد للنتائج
        folder_id = drive.create_folder("IDOR_Hunter_Results")
        
        # رفع ملف صغير
        test_file = "test_upload.txt"
        with open(test_file, 'w') as f:
            f.write("IDOR Hunter test file")
        
        if folder_id:
            drive.upload_file(test_file, folder_id)
    
    print("="*60)
