import os
import google.generativeai as genai

# در محیط Streamlit Cloud نیازی به dotenv نیست چون Secrets خودکار بارگذاری می‌شوند
# دریافت کلید مستقیماً از تنظیمات سرور
API_KEY = os.getenv("GOOGLE_API_KEY")

# تنظیمات اولیه گوگل
if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(messages, pdf_text=""):
    """
    تولید پاسخ با استفاده از مدل Gemini 1.5 Flash
    """
    if not API_KEY:
        return "❌ خطا: کلید API گوگل تنظیم نشده است. لطفاً در بخش Secrets مقدار GOOGLE_API_KEY را وارد کنید."

    try:
        # فراخوانی مدل جمینای
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # ترکیب متن PDF و سوال کاربر
        context_info = f"متن استخراج شده از فایل PDF:\n{pdf_text}\n\n" if pdf_text else ""
        user_query = messages[-1]["content"]
        
        full_prompt = (
            f"شما یک دستیار هوشمند هستید. بر اساس متن زیر به سوال کاربر پاسخ دقیق بده.\n"
            f"{context_info}"
            f"سوال کاربر: {user_query}"
        )

        # ارسال به گوگل
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "⚠️ هوش مصنوعی پاسخی تولید نکرد."

    except Exception as e:
        return f"❌ خطا در اتصال به Gemini: {str(e)}"

def extract_important_sentences(text):
    """
    تابع کمکی برای جلوگیری از خطای ایمپورت در فایل اصلی
    """
    if not text:
        return []
    # جدا کردن جملات بر اساس نقطه و فیلتر کردن جملات کوتاه
    sentences = text.split('.')
    return [s.strip() for s in sentences if len(s.strip()) > 20][:5]
