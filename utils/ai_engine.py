import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# تنظیمات گوگل جمینای
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size=1800, overlap=250):
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunks.append(text[i:i + chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks

def score_chunk(chunk: str, query: str) -> int:
    c = normalize_text(chunk)
    q = normalize_text(query)
    words = [w for w in q.split() if len(w) >= 2]
    score = 0
    for w in words:
        score += c.count(w)
    return score

def retrieve_relevant(document_text: str, query: str, top_k=4) -> str:
    chunks = chunk_text(document_text, chunk_size=1800, overlap=250)
    scored = [(score_chunk(ch, query), ch) for ch in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [ch for sc, ch in scored[:top_k] if sc > 0]
    if not picked:
        picked = chunks[:2]
    return "\n\n".join(picked)

def generate_chat_response(messages, document_text: str):
    if not API_KEY:
        return "❌ کلید API گوگل (GOOGLE_API_KEY) در Secrets یافت نشد."
    
    user_query = messages[-1]["content"]
    relevant_text = retrieve_relevant(document_text, user_query, top_k=4)

    system_instruction = (
        "شما یک دستیار آموزشی خیلی دقیق و حرفه‌ای هستید.\n"
        "قانون اصلی: فقط بر اساس «متن مرجع مرتبط» پاسخ بده.\n"
        "اگر پاسخ در متن مرجع نیست، بنویس: «این پاسخ در فایل یافت نشد.»\n"
        "پاسخ‌ها فارسی، ساخت‌یافته و حرفه‌ای باشند.\n"
    )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_instruction}\n\nمتن مرجع:\n{relevant_text}\n\nسوال کاربر: {user_query}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ خطای هوش مصنوعی: {str(e)}"

def extract_important_sentences(document_text: str):
    if not API_KEY: return []
    short_text = (document_text or "")[:6000]
    prompt = f"از متن زیر 5 نکته مهم برای امتحان استخراج کن. خروجی فارسی و شماره‌دار باشد:\n\n{short_text}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        lines = [l.strip() for l in response.text.split("\n") if l.strip()]
        return lines[:5]
    except Exception:
        return ["نکته‌ای استخراج نشد."]
