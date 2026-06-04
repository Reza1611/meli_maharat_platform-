import os
import google.generativeai as genai
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# دریافت کلید از Secrets
API_KEY = os.getenv("GOOGLE_API_KEY")

# تنظیمات اولیه گوگل
if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(messages, pdf_text=""):
    """
    تولید پاسخ با استفاده از مدل Gemini 1.5 Flash
    """
    if not API_KEY:
        return "❌ خطا: کلید API گوگل تنظیم نشده است در بخش Secrets."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context_info = f"متن استخراج شده از فایل PDF:\n{pdf_text}\n\n" if pdf_text else ""
        user_query = messages[-1]["content"]
        
        full_prompt = (
            f"شما یک دستیار هوشمند هستید. بر اساس متن زیر به سوال کاربر پاسخ دقیق بده.\n"
            f"{context_info}"
            f"سوال کاربر: {user_query}"
        )

        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "⚠️ هوش مصنوعی پاسخی تولید نکرد."

    except Exception as e:
        return f"❌ خطا در اتصال به Gemini: {str(e)}"

def extract_important_sentences(text):
    """
    تابع کمکی برای استخراج جملات کلیدی (برای جلوگیری از خطای ایمپورت)
    """
    if not text:
        return []
    sentences = text.split('.')
    return [s.strip() for s in sentences if len(s.strip()) > 20][:5]
