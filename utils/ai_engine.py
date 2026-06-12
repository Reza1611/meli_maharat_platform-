import streamlit as st
from openai import OpenAI
import re
import time

# تنظیمات کلاینت - کلید خود را اینجا چک کنید
API_KEY = "sk-k4ZiAJxRmxia4xD0rDb2cX3NAU9WAFp0X4cUHnzjn3lkGmUU"

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=API_KEY
)

MODEL_NAME = "gpt-4o"

def test_api_key():
    """تست اتصال به سرور API"""
    try:
        # تست با یک درخواست بسیار کوچک
        client.models.list()
        return True
    except Exception as e:
        st.sidebar.error(f"خطای اتصال به API: {str(e)}")
        return False

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def retrieve_relevant(document_text: str, query: str) -> str:
    if not document_text:
        return ""
    # تقسیم متن به بخش‌های کوچکتر برای جستجو
    chunks = [document_text[i:i+2000] for i in range(0, len(document_text), 1500)]
    q = normalize_text(query)
    words = [w for w in q.split() if len(w) > 2]
    
    scored_chunks = []
    for ch in chunks:
        score = sum(1 for w in words if w in normalize_text(ch))
        scored_chunks.append((score, ch))
    
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [c[1] for c in scored_chunks[:3] if c[0] > 0]
    
    return "\n\n".join(top_chunks) if top_chunks else document_text[:3000]

def generate_chat_response(messages, document_text: str):
    try:
        user_query = messages[-1]["content"]
        context = retrieve_relevant(document_text, user_query)
        
        sys_prompt = f"شما دستیار هوشمند دانشگاه ملی مهارت هستید. فقط بر اساس مستندات زیر پاسخ دهید. اگر پاسخ در متن نبود، بگویید در اسناد یافت نشد.\n\nمستندات:\n{context}"
        
        api_messages = [{"role": "system", "content": sys_prompt}] + messages[-5:]

        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=api_messages,
            temperature=0.4
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ متأسفانه خطایی در پردازش پاسخ رخ داد: {str(e)}"

def extract_important_sentences(text: str):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"پنج مورد از مهم‌ترین نکات متن زیر را به صورت فهرست‌وار استخراج کن:\n\n{text[:4000]}"}]
        )
        return resp.choices[0].message.content.split('\n')
    except:
        return ["تحلیل خودکار نکات کلیدی فعلاً در دسترس نیست."]
