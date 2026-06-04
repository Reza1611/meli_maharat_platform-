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
        return "❌ خطا: کلید API گوگل تنظیم نشده است."

    try:
        # استفاده از مدل فلش که برای متن‌های طولانی عالی و رایگان است
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # آماده‌سازی محتوا
        # جمینای محدودیت ۱۰۰ صفحه را به راحتی هندل می‌کند
        context_info = f"متن استخراج شده از فایل PDF:\n{pdf_text}\n\n" if pdf_text else ""
        user_query = messages[-1]["content"]
        
        full_prompt = (
            f"شما یک دستیار هوشمند هستید. بر اساس متن زیر به سوال کاربر پاسخ دقیق بده.\n"
            f"{context_info}"
            f"سوال کاربر: {user_query}"
        )

        # ارسال درخواست به گوگل
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "⚠️ هوش مصنوعی پاسخی تولید نکرد. دوباره تلاش کنید."

    except Exception as e:
        return f"❌ خطا در اتصال به Gemini: {str(e)}"
3. روی **Commit changes** کلیک کن.

---

### مرحله ۴: اصلاح فایل `main.py`
باید مطمئن شویم که در فایل اصلی، متغیرها درست فرستاده می‌شوند:
1. فایل **`main.py`** را باز کن.
2. در حدود خط ۱۳۵ (جایی که چت شروع می‌شود)، چک کن که فراخوانی تابع به این صورت باشد:
```python
   # این خط باید به این شکل باشد
   response = generate_chat_response(st.session_state.messages, st.session_state.pdf_text)
   
