import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(messages, pdf_text=""):
    if not API_KEY:
        return "❌ خطا: کلید API یافت نشد."
    try:
        # تغییر نام مدل به نسخه پایدار برای رفع خطای 404
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # بهبود ساختار درخواستی برای پاسخ دهی بهتر
        context_info = f"متن استخراج شده از فایل PDF:\n{pdf_text}\n\n" if pdf_text else ""
        user_query = messages[-1]["content"]
        
        system_instruction = "شما یک دستیار هوشمند هستید. با دقت به سوالات بر اساس متن داده شده پاسخ فارسی دهید."
        full_prompt = f"{system_instruction}\n\n{context_info}\n\nسوال کاربر: {user_query}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        # نمایش دقیق‌تر خطا برای عیب‌یابی
        return f"خطا در هوش مصنوعی: {str(e)}"

def extract_important_sentences(text):
    if not text: return []
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    return sentences[:5]
