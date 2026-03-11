"""
github_scanner.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - GitHub Scanner (Agent 1)
────────────────────────────────────────────────────────────────────
"""

import os
import json
import time
import base64
from datetime import datetime
from pathlib import Path

# محاولة استيراد PyGithub
try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("⚠️ PyGithub غير مثبت. جاري التثبيت...")
    os.system("pip install PyGithub")
    try:
        from github import Github, GithubException
        GITHUB_AVAILABLE = True
    except:
        print("❌ فشل تثبيت PyGithub. ثبته يدوياً: pip install PyGithub")
        GITHUB_AVAILABLE = False

# محاولة استيراد python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv غير مثبت. جاري التثبيت...")
    os.system("pip install python-dotenv")
    try:
        from dotenv import load_dotenv
        DOTENV_AVAILABLE = True
    except:
        print("❌ فشل تثبيت python-dotenv. ثبته يدوياً: pip install python-dotenv")
        DOTENV_AVAILABLE = False

# تحميل المتغيرات من .env
if DOTENV_AVAILABLE:
    load_dotenv()

class GitHubScanner:
    """
    ماسح GitHub - يبحث عن مشاريع وملفات تحتوي على IDOR
    """
    
    def __init__(self):
        """تهيئة الماسح باستخدام GitHub Token"""
        self.token = os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            print("❌ GITHUB_TOKEN غير موجود في ملف .env")
            print("💡 أضف السطر: GITHUB_TOKEN=\"your_token_here\"")
            self.github = None
            return
        
        if not GITHUB_AVAILABLE:
            print("❌ PyGithub غير متوفر. لن يعمل الماسح.")
            self.github = None
            return
        
        try:
            self.github = Github(self.token)
            # اختبار الاتصال
            user = self.github.get_user()
            print(f"✅ تم الاتصال بـ GitHub - المستخدم: {user.login}")
            
            # عرض معدل الطلبات المتبقي
            rate_limit = self.github.get_rate_limit()
            print(f"📊 باقي {rate_limit.core.remaining} طلب من {rate_limit.core.limit}")
            
        except GithubException as e:
            print(f"❌ خطأ في الاتصال بـ GitHub: {e}")
            self.github = None
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            self.github = None
    
    def search_code(self, query="idor", language=None, max_results=30):
        """
        البحث عن كود في GitHub
        ─────────────────────
        query: كلمة البحث (مثل "idor", "insecure direct object")
        language: لغة البرمجة (مثل "python", "javascript")
        max_results: أقصى عدد من النتائج
        """
        if not self.github:
            print("❌ GitHub غير مهيأ")
            return []
        
        # بناء الاستعلام
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        print(f"\n🔍 بحث في GitHub عن: {search_query}")
        
        results = []
        try:
            # البحث في الكود
            code_results = self.github.search_code(search_query)
            
            print(f"📊 إجمالي النتائج المتاحة: {code_results.totalCount}")
            
            count = 0
            for item in code_results:
                if count >= max_results:
                    break
                
                try:
                    # معلومات أساسية
                    repo_name = item.repository.full_name
                    file_name = item.name
                    file_path = item.path
                    file_url = item.html_url
                    
                    # محاولة جلب المحتوى (اختياري، قد يبطئ البحث)
                    content_snippet = None
                    try:
                        if hasattr(item, 'content') and item.content:
                            # فك تشفير base64
                            decoded = base64.b64decode(item.content).decode('utf-8', errors='ignore')
                            content_snippet = decoded[:300] + "..." if len(decoded) > 300 else decoded
                    except:
                        pass
                    
                    result = {
                        "file_name": file_name,
                        "path": file_path,
                        "repository": repo_name,
                        "url": file_url,
                        "language": language,
                        "content_snippet": content_snippet,
                        "search_query": search_query
                    }
                    
                    results.append(result)
                    count += 1
                    
                    if count % 10 == 0:
                        print(f"   ✅ تم جمع {count} نتيجة...")
                    
                except Exception as e:
                    print(f"⚠️ خطأ في معالجة ملف: {e}")
                
                # تأخير بسيط تجنباً للمشاكل
                time.sleep(0.2)
            
            print(f"✅ تم العثور على {len(results)} نتيجة (من أصل {code_results.totalCount})")
            
        except GithubException as e:
            print(f"⚠️ خطأ في البحث: {e}")
            print(f"   الرمز: {e.status}, الرسالة: {e.data}")
        except Exception as e:
            print(f"⚠️ خطأ غير متوقع: {e}")
        
        return results
    
    def search_repositories(self, query="idor vulnerability", sort="stars", max_results=20):
        """
        البحث عن مستودعات
        ─────────────────
        query: كلمة البحث
        sort: الترتيب (stars, forks, updated)
        max_results: أقصى عدد من النتائج
        """
        if not self.github:
            print("❌ GitHub غير مهيأ")
            return []
        
        print(f"\n🔍 بحث عن مستودعات: {query}")
        
        results = []
        try:
            repos = self.github.search_repositories(query, sort=sort)
            
            print(f"📊 إجمالي المستودعات: {repos.totalCount}")
            
            count = 0
            for repo in repos:
                if count >= max_results:
                    break
                
                result = {
                    "name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "created_at": str(repo.created_at),
                    "updated_at": str(repo.updated_at),
                    "search_query": query
                }
                
                results.append(result)
                count += 1
                
                if count % 5 == 0:
                    print(f"   ✅ {count} مستودع...")
            
            print(f"✅ تم العثور على {len(results)} مستودع")
            
        except GithubException as e:
            print(f"⚠️ خطأ في البحث: {e}")
        
        return results
    
    def get_file_content(self, repo_name, file_path):
        """
        جلب محتوى ملف محدد من مستودع
        ────────────────────────────
        repo_name: اسم المستودع (مثل "owner/repo")
        file_path: مسار الملف داخل المستودع
        """
        if not self.github:
            return None
        
        try:
            repo = self.github.get_repo(repo_name)
            contents = repo.get_contents(file_path)
            
            if contents.encoding == "base64":
                content = base64.b64decode(contents.content).decode('utf-8', errors='ignore')
                return content
            else:
                return contents.content
        except Exception as e:
            print(f"⚠️ خطأ في جلب الملف: {e}")
            return None
    
    def save_results(self, data, filename="github_results.json"):
        """حفظ النتائج في ملف JSON"""
        if not data:
            print("⚠️ لا توجد نتائج للحفظ")
            return None
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "total": len(data),
            "results": data
        }
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"✅ تم حفظ {len(data)} نتيجة في {filename}")
            return filename
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {e}")
            return None


# اختبار سريع
if __name__ == "__main__":
    print("="*60)
    print("🐙 GitHub Scanner - IDOR Hunter")
    print("="*60)
    
    # تهيئة الماسح
    scanner = GitHubScanner()
    
    if scanner.github:
        print("\n📝 اختبار البحث عن كود IDOR...")
        
        # البحث عن كود في Python
        code_results = scanner.search_code(
            query="idor",
            language="python",
            max_results=10
        )
        
        # البحث عن مستودعات
        repo_results = scanner.search_repositories(
            query="idor vulnerability",
            max_results=5
        )
        
        # دمج وحفظ النتائج
        all_results = {
            "code_results": code_results,
            "repository_results": repo_results
        }
        
        scanner.save_results(all_results, "github_idor_results.json")
        
        # عرض ملخص
        print("\n📊 ملخص النتائج:")
        print(f"   🔍 كود: {len(code_results)} ملف")
        print(f"   📦 مستودعات: {len(repo_results)} مستودع")
    
    print("\n" + "="*60)
