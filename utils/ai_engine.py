import streamlit as st
import google.generativeai as genai
import re
import time

# تنظیمات گوگل جمینای
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # استفاده از نسخه سریع فلش

# ---------------------------
# نرمال‌سازی متن
# ---------------------------
def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------------
# تکه‌تکه کردن متن (بدون تغییر)
# ---------------------------
def chunk_text(text: str, chunk_size=1800, overlap=250):
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunks.append(text[i:i + chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks

# ---------------------------
# امتیازدهی و بازیابی (بدون تغییر)
# ---------------------------
def score_chunk(chunk: str, query: str) -> int:
    c = normalize_text(chunk)
    q = normalize_text(query)
    words = [w for w in q.split() if len(w) >= 2]
    score = sum(c.count(w) for w in words)
    return score

def retrieve_relevant(document_text: str, query: str, top_k=4) -> str:
    chunks = chunk_text(document_text, chunk_size=1800, overlap=250)
    scored = [(score_chunk(ch, query), ch) for ch in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [ch for sc, ch in scored[:top_k] if sc > 0]
    if not picked:
        picked = chunks[:2]
    return "\n\n".join(picked)

# ---------------------------
# تولید پاسخ با Gemini (اصلاح شده)
# ---------------------------
def generate_chat_response(messages, document_text: str):
    user_query = messages[-1]["content"]
    relevant_text = retrieve_relevant(document_text, user_query, top_k=4)

    prompt = f"""
    شما یک دستیار آموزشی دقیق هستید. فقط بر اساس متن مرجع زیر پاسخ دهید.
    اگر پاسخ در متن نیست، بگویید: «این پاسخ به‌صورت مستقیم در فایل یافت نشد.»
    
    متن مرجع:
    {relevant_text}
    
    سوال کاربر: {user_query}
    """

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return f"❌ خطا در اتصال به گوگل: {str(e)}"

# ---------------------------
# استخراج نکات مهم با Gemini (اصلاح شده)
# ---------------------------
def extract_important_sentences(document_text: str):
    short_text = (document_text or "")[:8000]
    prompt = f"از متن زیر 5 نکته مهم و کاربردی استخراج کن. خروجی شماره‌دار و فارسی باشد:\n\n{short_text}"

    try:
        response = model.generate_content(prompt)
        lines = [l.strip() for l in response.text.split("\n") if l.strip()]
        return lines[:5]
    except:
        return ["❌ تحلیل سند با مدل گوگل انجام نشد."]
