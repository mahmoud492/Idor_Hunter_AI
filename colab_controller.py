"""
colab_controller.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - Google Colab Controller
────────────────────────────────────────────────────────────────────
"""

import os
import time
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from simple_accounts import SimpleAccounts
from drive_manager import DriveManager

class ColabController:
    """
    مدير Google Colab - تشغيل وإدارة Notebooks لجميع الحسابات
    """
    
    def __init__(self):
        self.accounts = SimpleAccounts()
        self.drive_managers = []
        self.notebooks = []
        self.results_folder = "IDOR_Hunter_Colab_Results"
        
        print("="*60)
        print("🚀 Google Colab Controller - IDOR Hunter")
        print("="*60)
        
        # ربط Drive لكل حساب
        for i in range(self.accounts.get_count()):
            print(f"\n📧 Connecting account {i+1}/{self.accounts.get_count()}...")
            dm = DriveManager(account_index=i)
            if dm.service:
                self.drive_managers.append(dm)
                print(f"✅ Account {i+1} connected to Drive")
    
    def create_notebook(self, account_index: int = 0) -> Optional[str]:
        """
        إنشاء Notebook جديد في Drive
        """
        if account_index >= len(self.drive_managers):
            print(f"❌ Account {account_index} not connected")
            return None
        
        dm = self.drive_managers[account_index]
        account = self.accounts.get_account(account_index)
        
        print(f"\n📝 Creating notebook for {account['email']}...")
        
        # محتوى Notebook
        notebook_content = f'''{{
  "cells": [
    {{
      "cell_type": "markdown",
      "metadata": {{}},
      "source": [
        "# 🚀 IDOR Hunter Scanner\\n",
        "---\\n",
        f"**Account:** {account['email']}\\n",
        f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n",
        f"**Target:** https://neon.tech\\n",
        "---\\n"
      ]
    }},
    {{
      "cell_type": "code",
      "execution_count": null,
      "metadata": {{}},
      "source": [
        "# 1. Install requirements\\n",
        "!pip install requests pycryptodome python-dotenv beautifulsoup4 tweepy github3.py\\n",
        "\\n",
        "print('✅ Libraries installed')\\n"
      ]
    }},
    {{
      "cell_type": "code",
      "execution_count": null,
      "metadata": {{}},
      "source": [
        "# 2. Clone the project\\n",
        "!git clone https://github.com/mahmoud492/Idor_Hunter_AI.git\\n",
        "%cd Idor_Hunter_AI\\n",
        "\\n",
        "print('✅ Project cloned')\\n"
      ]
    }},
    {{
      "cell_type": "code",
      "execution_count": null,
      "metadata": {{}},
      "source": [
        "# 3. Run scanner on neon.tech\\n",
        "!python orchestrator.py\\n",
        "\\n",
        "print('✅ Scan completed')\\n"
      ]
    }},
    {{
      "cell_type": "markdown",
      "metadata": {{}},
      "source": [
        "## 📊 Results\\n",
        "The scan results will be saved in the current directory.\\n",
        "Check `idor_analysis_result.json` for detailed findings.\\n"
      ]
    }}
  ],
  "metadata": {{
    "kernelspec": {{
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }},
    "language_info": {{
      "name": "python",
      "version": "3.11.0"
    }}
  }},
  "nbformat": 4,
  "nbformat_minor": 4
}}
'''
        
        # حفظ الملف محلياً
        local_file = f"notebook_account_{account_index}.ipynb"
        with open(local_file, 'w', encoding='utf-8') as f:
            f.write(notebook_content)
        
        # إنشاء مجلد للنتائج في Drive
        folder_id = dm.create_folder(self.results_folder)
        if folder_id:
            # رفع Notebook إلى Drive
            file_name = f"IDOR_Scanner_{account['email'].split('@')[0]}.ipynb"
            file_id = dm.upload_file(local_file, folder_id, file_name)
            
            if file_id:
                self.notebooks.append({
                    "account_index": account_index,
                    "email": account['email'],
                    "file_id": file_id,
                    "local_file": local_file,
                    "folder_id": folder_id,
                    "url": f"https://colab.research.google.com/drive/{file_id}"
                })
                print(f"✅ Notebook created for {account['email']}")
                return file_id
        
        return None
    
    def create_all_notebooks(self) -> List[str]:
        """
        إنشاء Notebooks لجميع الحسابات
        """
        print("\n" + "="*60)
        print("📦 Creating notebooks for all accounts...")
        print("="*60)
        
        file_ids = []
        for i in range(len(self.drive_managers)):
            file_id = self.create_notebook(i)
            if file_id:
                file_ids.append(file_id)
            time.sleep(2)  # تجنب rate limits
        
        print(f"\n✅ Created {len(file_ids)} notebooks")
        return file_ids
    
    def list_notebooks(self):
        """
        عرض جميع Notebooks
        """
        if not self.notebooks:
            print("❌ No notebooks created yet")
            return
        
        print("\n" + "="*60)
        print("📊 Google Colab Notebooks")
        print("="*60)
        
        for i, nb in enumerate(self.notebooks, 1):
            print(f"\n{i}. 📧 {nb['email']}")
            print(f"   🔗 {nb['url']}")
    
    def open_notebook(self, index: int = 0):
        """
        فتح Notebook في المتصفح
        """
        if not self.notebooks or index >= len(self.notebooks):
            print("❌ Notebook not found")
            return
        
        nb = self.notebooks[index]
        try:
            webbrowser.open(nb['url'])
            print(f"🌐 Opened {nb['email']}'s notebook")
        except:
            print(f"📋 Copy this URL: {nb['url']}")
    
    def open_all_notebooks(self):
        """
        فتح جميع Notebooks
        """
        print("\n" + "="*60)
        print("🔗 Open these notebooks and run them:")
        print("="*60)
        
        for i, nb in enumerate(self.notebooks):
            print(f"\n{i+1}. 📧 {nb['email']}")
            print(f"   {nb['url']}")
            try:
                webbrowser.open(nb['url'])
                time.sleep(1)
            except:
                pass
    
    def save_state(self, filename="colab_state.json"):
        """
        حفظ حالة Notebooks
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "notebooks": self.notebooks,
            "results_folder": self.results_folder
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"\n✅ State saved to {filename}")
    
    def load_state(self, filename="colab_state.json") -> bool:
        """
        تحميل حالة Notebooks
        """
        if not os.path.exists(filename):
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.notebooks = state.get("notebooks", [])
        self.results_folder = state.get("results_folder", "IDOR_Hunter_Colab_Results")
        
        print(f"\n✅ Loaded {len(self.notebooks)} notebooks from state")
        return True
    
    def run_all(self):
        """
        التشغيل الكامل: إنشاء Notebooks وعرضها
        """
        if not self.drive_managers:
            print("❌ No Drive connections available")
            return
        
        # إنشاء Notebooks
        self.create_all_notebooks()
        
        # عرض النتائج
        self.list_notebooks()
        
        # حفظ الحالة
        self.save_state()
        
        # فتح جميع Notebooks
        print("\n" + "="*60)
        print("🌐 Opening notebooks in browser...")
        print("="*60)
        self.open_all_notebooks()


# اختبار
if __name__ == "__main__":
    controller = ColabController()
    
    if controller.drive_managers:
        controller.run_all()
    
    print("\n" + "="*60)
    print("✅ Colab Controller completed successfully!")
    print("="*60)
