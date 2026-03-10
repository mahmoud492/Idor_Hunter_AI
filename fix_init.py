import re

# قراءة الملف
with open('accounts_manager.py', 'r') as f:
    content = f.read()

# التأكد من وجود self._load_accounts() في __init__
if 'self._load_accounts()' not in content:
    # إضافته بعد تحميل env loader
    content = content.replace(
        '        if ENV_AVAILABLE:\n            self.env = EnvLoader()\n        else:\n            self.env = None',
        '        if ENV_AVAILABLE:\n            self.env = EnvLoader()\n        else:\n            self.env = None\n        \n        # تحميل الحسابات\n        self._load_accounts()'
    )
    
    # حفظ الملف
    with open('accounts_manager.py', 'w') as f:
        f.write(content)
    print("✅ تم تعديل __init__ بنجاح!")
else:
    print("✅ __init__ يحتوي بالفعل على self._load_accounts()")
