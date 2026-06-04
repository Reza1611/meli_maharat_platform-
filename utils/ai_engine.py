import os
import re
import google.generativeai as genai
import streamlit as st

# تنظیمات اتصال به Gemini با استفاده از Secrets استریم‌لیت
def get_api_key():
    # اول در سکرت‌های استریم‌لیت چک می‌کند (برای سرور)
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    # سپس در متغیرهای محیطی چک می‌کند (برای تست لوکال)
    return os.getenv("GOOGLE_API_KEY")

API_KEY = get_api_key()

if API_KEY:
    genai.configure(api_key=API_KEY)

def normalize_text(text: str) -> str:
    """استانداردسازی متن برای بهبود جستجو"""
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    # حذف کاراکترهای خاص غیر از حروف و اعداد فارسی/انگلیسی
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size=1800, overlap=250):
    """تکه تکه کردن متن‌های طولانی برای پردازش بهتر"""
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunks.append(text[i:i + chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks

def score_chunk(chunk: str, query: str) -> int:
    """امتیازدهی به هر تکه بر اساس شباهت به سوال کاربر"""
    c = normalize_text(chunk)
    q = normalize_text(query)
    words = [w for w in q.split() if len(w) >= 2]
    score = 0
    for w in words:
        if w in c:
            score += c.count(w)
    return score

def retrieve_relevant(document_text: str, query: str, top_k=4) -> str:
    """یافتن مرتبط‌ترین بخش‌های فایل برای ارسال به هوش مصنوعی"""
    if not document_text:
        return ""
    
    chunks = chunk_text(document_text, chunk_size=1800, overlap=250)
    scored = [(score_chunk(ch, query), ch) for ch in chunks]
    # مرتب‌سازی بر اساس امتیاز بیشتر
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # انتخاب تکه‌هایی که حداقل یک کلمه مشترک دارند
    picked = [ch for sc, ch in scored[:top_k] if sc > 0]
    
    if not picked:
        # اگر هیچ کلمه مشترکی نبود، دو تکه اول را به عنوان پیش‌فرض برمی‌گرداند
        picked = chunks[:2]
        
    return "\n\n".join(picked)

def generate_chat_response(messages, document_text: str):
    """تولید پاسخ توسط مدل Gemini 1.5 Flash"""
    if not API_KEY:
        return "❌ خطا: کلید GOOGLE_API_KEY در بخش Secrets تنظیم نشده است."
    
    # آخرین سوال کاربر
    user_query = messages[-1]["content"]
    
    # بازیابی بخش‌های مرتبط از فایل PDF
    relevant_text = retrieve_relevant(document_text, user_query, top_k=4)

    system_instruction = (
        "شما یک دستیار هوشمند برای تحلیل فایل‌های آموزشی هستید.\n"
        "وظیفه شما پاسخ دقیق به سوالات کاربر بر اساس 'متن مرجع' ارائه شده است.\n"
        "قوانین:\n"
        "1. فقط بر اساس متن مرجع پاسخ بده.\n"
        "2. اگر پاسخ در متن نیست، بگو: 'متأسفانه پاسخ این سوال در فایل یافت نشد.'\n"
        "3. پاسخ‌ها را به صورت فارسی، خوانا و با استفاده از بولت‌پوینت (در صورت نیاز) بنویس.\n"
    )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_instruction}\n\nمتن مرجع از فایل:\n{relevant_text}\n\nسوال کاربر:\n{user_query}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ خطای ارتباط با هوش مصنوعی: {str(e)}"

def extract_important_sentences(document_text: str):
    """استخراج نکات مهم برای نمایش در داشبورد"""
    if not API_KEY or not document_text:
        return ["نکته‌ای برای نمایش وجود ندارد."]
    
    # محدود کردن متن برای سرعت بیشتر در استخراج اولیه
    short_text = document_text[:6000]
    prompt = f"بر اساس متن زیر، 5 مورد از مهم‌ترین نکات کلیدی و امتحانی را به صورت جملات کوتاه و شماره‌دار استخراج کن:\n\n{short_text}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        # جدا کردن خطوط و تمیز کردن آن‌ها
        lines = [l.strip() for l in response.text.split("\n") if l.strip()]
        return lines[:5]
    except Exception:
        return ["خطا در استخراج نکات مهم."]
