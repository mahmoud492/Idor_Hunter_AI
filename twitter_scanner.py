"""
twitter_scanner.py
────────────────────────────────────────────────────────────────────
IDOR Hunter - Twitter Scanner (Agent 1)
────────────────────────────────────────────────────────────────────
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# محاولة استيراد tweepy (مكتبة تويتر)
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("⚠️ tweepy غير مثبت. جاري التثبيت...")
    os.system("pip install tweepy")
    import tweepy
    TWEEPY_AVAILABLE = True

# محاولة استيراد python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv غير مثبت. جاري التثبيت...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True

# تحميل المتغيرات من .env
load_dotenv()

class TwitterScanner:
    """
    ماسح تويتر - يبحث عن تغريدات تحتوي على IDOR
    """
    
    def __init__(self):
        """تهيئة الماسح بمفاتيح API من .env"""
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        # التحقق من وجود المفاتيح
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("❌ مفقود بعض مفاتيح Twitter API. تأكد من ملف .env")
            self.client = None
            return
        
        # تهيئة العميل (الإصدار الجديد من tweepy)
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
                wait_on_rate_limit=True
            )
            print("✅ تم الاتصال بتويتر بنجاح")
        except Exception as e:
            print(f"❌ فشل الاتصال بتويتر: {e}")
            self.client = None
    
    def search_idor_tweets(self, query="#IDOR", max_results=100, days_back=7):
        """
        البحث عن تغريدات تحتوي على كلمات مفتاحية
        ──────────────────────────────────────
        query: كلمة البحث (مثل "#IDOR")
        max_results: أقصى عدد من النتائج
        days_back: البحث عن تغريدات آخر X يوم
        """
        if not self.client:
            print("❌ العميل غير مهيأ")
            return []
        
        # حساب التاريخ
        start_time = datetime.utcnow() - timedelta(days=days_back)
        
        # كلمات بحث إضافية
        queries = [
            f"{query} -is:retweet",
            f"IDOR vulnerability -is:retweet",
            f"broken access control -is:retweet",
            f"bugbounty IDOR -is:retweet"
        ]
        
        all_tweets = []
        
        for q in queries:
            try:
                print(f"🔍 بحث عن: {q}")
                
                response = self.client.search_recent_tweets(
                    query=q,
                    max_results=min(max_results, 100),  # API يسمح بحد أقصى 100
                    tweet_fields=["created_at", "public_metrics", "author_id"],
                    expansions=["author_id"],
                    start_time=start_time
                )
                
                if response.data:
                    tweets = []
                    for tweet in response.data:
                        tweets.append({
                            "id": tweet.id,
                            "text": tweet.text,
                            "created_at": str(tweet.created_at),
                            "author_id": tweet.author_id,
                            "likes": tweet.public_metrics["like_count"],
                            "retweets": tweet.public_metrics["retweet_count"],
                            "query": q
                        })
                    
                    all_tweets.extend(tweets)
                    print(f"✅ وجد {len(tweets)} تغريدة")
                
                time.sleep(2)  # تجنب تجاوز rate limits
                
            except Exception as e:
                print(f"⚠️ خطأ في البحث: {e}")
        
        return all_tweets
    
    def search_by_users(self, usernames=["nahamsec", "stokfredrik", "tomnomnom", "insiderphd"], max_results=50):
        """
        البحث في تغريدات مستخدمين معينين
        ────────────────────────────────
        usernames: قائمة بأسماء المستخدمين
        """
        if not self.client:
            return []
        
        all_tweets = []
        
        for username in usernames:
            try:
                print(f"🔍 جلب تغريدات {username}")
                
                # الحصول على user ID
                user = self.client.get_user(username=username)
                if not user.data:
                    continue
                
                user_id = user.data.id
                
                # جلب تغريدات المستخدم
                response = self.client.get_users_tweets(
                    id=user_id,
                    max_results=min(max_results, 100),
                    tweet_fields=["created_at", "public_metrics"],
                    exclude=["retweets", "replies"]
                )
                
                if response.data:
                    tweets = []
                    for tweet in response.data:
                        tweets.append({
                            "id": tweet.id,
                            "text": tweet.text,
                            "created_at": str(tweet.created_at),
                            "author": username,
                            "likes": tweet.public_metrics["like_count"],
                            "retweets": tweet.public_metrics["retweet_count"]
                        })
                    
                    all_tweets.extend(tweets)
                    print(f"✅ وجد {len(tweets)} تغريدة من {username}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ خطأ في جلب تغريدات {username}: {e}")
        
        return all_tweets
    
    def save_results(self, tweets, filename="twitter_results.json"):
        """حفظ النتائج في ملف JSON"""
        if not tweets:
            print("⚠️ لا توجد نتائج للحفظ")
            return
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total": len(tweets),
            "tweets": tweets
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ تم حفظ {len(tweets)} تغريدة في {filename}")
        return filename


# اختبار سريع
if __name__ == "__main__":
    print("="*60)
    print("🐦 Twitter Scanner - IDOR Hunter")
    print("="*60)
    
    scanner = TwitterScanner()
    
    if scanner.client:
        # بحث عن #IDOR
        tweets = scanner.search_idor_tweets(query="#IDOR", max_results=20, days_back=3)
        
        # بحث في حسابات خبراء
        expert_tweets = scanner.search_by_users(
            usernames=["nahamsec", "stokfredrik", "insiderphd"],
            max_results=10
        )
        
        # دمج النتائج
        all_tweets = tweets + expert_tweets
        
        if all_tweets:
            scanner.save_results(all_tweets, "twitter_idor_results.json")
            
            print("\n📊 أول 5 تغريدات:")
            for i, tweet in enumerate(all_tweets[:5]):
                print(f"\n{i+1}. {tweet['text'][:100]}...")
                print(f"   👤 {tweet.get('author', tweet.get('author_id', 'غير معروف'))}")
                print(f"   ❤️ {tweet.get('likes', 0)} | 🔁 {tweet.get('retweets', 0)}")
        else:
            print("❌ لم يتم العثور على نتائج")
    
    print("="*60)
