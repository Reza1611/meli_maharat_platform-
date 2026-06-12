import streamlit as st
from openai import OpenAI
import time

# تنظیمات با زمان انتظار بیشتر (Timeout)
API_KEY = "sk-k4ZiAJxRmxia4xD0rDb2cX3NAU9WAFp0X4cUHnzjn3lkGmUU"

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=API_KEY,
    timeout=45.0,  # افزایش زمان انتظار به ۴۵ ثانیه
    max_retries=3   # تلاش مجدد خودکار در صورت خطا
)

def test_api_key():
    try:
        client.models.list()
        return True
    except:
        return False

def generate_chat_response(messages, document_text: str):
    try:
        # انتخاب بخشی از متن (برای جلوگیری از سنگین شدن درخواست)
        context = document_text[:6000] 
        
        sys_prompt = f"شما دستیار دانشگاه هستید. فقط بر اساس متن زیر پاسخ دهید:\n{context}"
        
        # ارسال پیام‌ها
        api_messages = [{"role": "system", "content": sys_prompt}] + messages[-3:]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=api_messages,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        if "timeout" in str(e).lower():
            return "❌ زمان پاسخگویی سرور طولانی شد. لطفاً دوباره تلاش کنید."
        return f"❌ خطای فنی: {str(e)}"
