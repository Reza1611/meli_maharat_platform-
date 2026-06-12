from openai import OpenAI, APIConnectionError
import re
import time

# تنظیم کلاینت با تایم‌اوت بالاتر برای سرور
CLIENT = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key="sk-k4ZiAJxRmxia4xD0rDb2cX3NAU9WAFp0X4cUHnzjn3lkGmUU",
    timeout=60.0  # اضافه کردن تایم‌اوت ۶۰ ثانیه‌ای
)

MODEL_NAME = "gpt-4o"

def test_api_key():
    try:
        # استفاده از متد سبک‌تر برای تست اتصال
        CLIENT.models.list()
        return True
    except Exception as e:
        print(f"API Error: {e}")
        return False

def generate_chat_response(messages, document_text: str):
    user_query = messages[-1]["content"]
    # محدود کردن متن برای جلوگیری از سنگین شدن پردازش در سرور
    relevant_text = retrieve_relevant(document_text, user_query, top_k=3)

    system_instruction = (
        "شما یک دستیار آموزشی دقیق هستید. "
        "فقط بر اساس متن مرجع پاسخ بده. "
        "اگر پاسخ در فایل نیست، بگو یافت نشد."
    )

    api_messages = [
        {"role": "system", "content": system_instruction},
        {"role": "system", "content": f"متن مرجع:\n{relevant_text}"},
        *messages[-5:] # ارسال آخرین پیام‌ها برای حفظ حافظه کوتاه
    ]

    for attempt in range(3):
        try:
            resp = CLIENT.chat.completions.create(
                model=MODEL_NAME,
                messages=api_messages,
                temperature=0.2
            )
            return resp.choices[0].message.content
        except Exception:
            time.sleep(2)
            continue

    return "❌ متأسفانه ارتباط با سرور هوش مصنوعی برقرار نشد. لطفاً دوباره سوال خود را بپرسید."

# بقیه توابع (normalize, chunk, score, retrieve) دقیقاً مثل کد خودت بماند
