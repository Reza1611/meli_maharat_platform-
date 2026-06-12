from openai import OpenAI
import re
import time

# تنظیم کلاینت با Timeout مناسب
CLIENT = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key="sk-k4ZiAJxRmxia4xD0rDb2cX3NAU9WAFp0X4cUHnzjn3lkGmUU",
    timeout=60.0 # افزایش زمان برای جلوگیری از چرخیدن مداوم
)

MODEL_NAME = "gpt-4o"

def test_api_key():
    try:
        CLIENT.models.list()
        return True
    except: return False

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"\s+", " ", text).strip()

def retrieve_relevant(document_text: str, query: str) -> str:
    # بازیابی ساده شده برای سرعت بالاتر
    return document_text[:8000] 

def generate_chat_response(messages, document_text: str):
    relevant_text = retrieve_relevant(document_text, messages[-1]["content"])
    
    api_messages = [
        {"role": "system", "content": f"پاسخ را فقط از متن زیر استخراج کن:\n{relevant_text}"},
        *messages[-5:]
    ]

    for attempt in range(3):
        try:
            resp = CLIENT.chat.completions.create(
                model=MODEL_NAME,
                messages=api_messages,
                temperature=0.2
            )
            return resp.choices[0].message.content
        except Exception as e:
            time.sleep(2)
    return "❌ خطا در اتصال. لطفاً دوباره سوال خود را بپرسید."

def extract_important_sentences(document_text: str):
    try:
        resp = CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"5 نکته مهم از متن زیر بگو:\n{document_text[:4000]}"}]
        )
        return resp.choices[0].message.content.split("\n")
    except: return ["خطا در تحلیل"]
