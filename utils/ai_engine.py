import streamlit as st
from openai import OpenAI, APIConnectionError
import re
import time

# تنظیمات کلاینت با پشتیبانی از Secrets
API_KEY = st.secrets.get("GAPGPT_API_KEY", "sk-k4ZiAJxRmxia4xD0rDb2cX3NAU9WAFp0X4cUHnzjn3lkGmUU")
client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=API_KEY
)

MODEL_NAME = "gpt-4o"

def test_api_key():
    try:
        client.models.list()
        return True
    except Exception:
        return False

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size=1500, overlap=200):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += (chunk_size - overlap)
    return chunks

def retrieve_relevant(document_text: str, query: str) -> str:
    chunks = chunk_text(document_text)
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
    user_query = messages[-1]["content"]
    context = retrieve_relevant(document_text, user_query)
    
    sys_prompt = f"شما دستیار آموزشی هستید. فقط بر اساس متن زیر پاسخ دهید:\n{context}"
    
    api_messages = [{"role": "system", "content": sys_prompt}] + messages[-5:]

    for _ in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=api_messages,
                temperature=0.3
            )
            return resp.choices[0].message.content
        except Exception:
            time.sleep(1)
    return "❌ خطا در اتصال به هوش مصنوعی."

def extract_important_sentences(text: str):
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"5 نکته کلیدی از متن زیر استخراج کن:\n\n{text[:5000]}"}]
        )
        return resp.choices[0].message.content.split('\n')
    except:
        return ["تحلیل خودکار با خطا مواجه شد."]
