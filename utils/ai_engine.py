import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# تنظیمات کلاینت
API_KEY = os.getenv("sk-ocTcJv4Do6xWp5BItyoiAUmrFWoVJx6KCsP0JvkPEQaMRrK8")
MODEL_NAME = "gpt-4o-mini" # استفاده از این مدل برای Context بالاتر و هزینه کمتر
CLIENT = OpenAI(api_key=API_KEY)

def find_relevant_chunks(text, query, num_chunks=5):
    """
    پیدا کردن بخش‌های مرتبط از متن ۱۰۰ صفحه‌ای بر اساس سوال کاربر
    """
    if not text:
        return ""
    
    # تقسیم متن به تکه‌های ۲۰۰۰ کاراکتری (حدود ۲-۳ صفحه در هر تکه)
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    
    # یک جستجوی ساده برای پیدا کردن تکه‌هایی که کلمات کلیدی سوال را دارند
    query_words = query.lower().split()
    chunk_scores = []
    
    for chunk in chunks:
        score = sum(1 for word in query_words if word in chunk.lower())
        chunk_scores.append((score, chunk))
    
    # مرتب‌سازی بر اساس امتیاز و انتخاب بهترین تکه‌ها
    relevant_chunks = sorted(chunk_scores, key=lambda x: x[0], reverse=True)[:num_chunks]
    
    return "\n---\n".join([c[1] for c in relevant_chunks])

def generate_chat_response(messages, pdf_text=""):
    if not messages:
        return "سوالی دریافت نشد."

    user_query = messages[-1]["content"]
    
    # ۱. اگر متن طولانی است، فقط بخش‌های مرتبط را استخراج کن
    if pdf_text and len(pdf_text) > 20000:
        with_context = True
        context_text = find_relevant_chunks(pdf_text, user_query)
    else:
        with_context = True if pdf_text else False
        context_text = pdf_text

    # ۲. ساخت پیام سیستم
    system_instruction = (
        "شما یک دستیار پژوهشی هستید. با توجه به بخش‌های استخراج شده از یک فایل طولانی، "
        "به سوال کاربر پاسخ دهید. اگر پاسخ در این بخش‌ها نیست، بر اساس دانش خود راهنمایی کنید "
        "و بگویید که در مستندات صریحاً پیدا نشد."
    )

    api_messages = [{"role": "system", "content": system_instruction}]
    
    if with_context:
        api_messages.append({"role": "system", "content": f"Context from PDF:\n{context_text}"})

    # ۳. اضافه کردن تاریخچه چت (۳ پیام آخر)
    for msg in messages[-3:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        # ۴. ارسال به API با زمان انتظار بالا
        resp = CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=api_messages,
            temperature=0.3,
            timeout=80.0
        )
        return resp.choices[0].message.content
    except Exception as e:
        if "timeout" in str(e).lower():
            return "⚠️ پردازش فایل طولانی است. لطفا سوال دقیق‌تری بپرسید تا جستجو بهتر انجام شود."
        return f"❌ خطا: {str(e)}"
