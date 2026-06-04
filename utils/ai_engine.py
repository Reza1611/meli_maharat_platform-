import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# دریافت کلید از Secrets استریم‌لیت
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(messages, pdf_text=""):
    if not API_KEY:
        return "❌ خطا: کلید API یافت نشد. لطفاً در Secrets تنظیم کنید."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        context_info = f"متن فایل:\n{pdf_text}\n\n" if pdf_text else ""
        user_query = messages[-1]["content"]
        full_prompt = f"{context_info}سوال: {user_query}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"خطا در هوش مصنوعی: {str(e)}"

def extract_important_sentences(text):
    if not text: return []
    return [s.strip() for s in text.split('.') if len(s.strip()) > 20][:5]
