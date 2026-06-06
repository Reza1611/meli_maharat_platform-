import streamlit as st
from openai import OpenAI
import fitz  # کتابخانه PyMuPDF

# تنظیمات صفحه
st.set_page_config(page_title="Nexus AI - Meli Maharat", layout="wide")

# ۱. تعریف مستقیم کلاینت هوش مصنوعی
client = OpenAI(
    base_url="https://api.avalai.ir/v1",
    api_key="aa-OsqPM4WiwThkqS49P1p6cLRv22XMIJ4yKmAEhMIrq5HKKbYL"
)

# ۲. تابع استخراج متن از PDF (نسخه مقاوم به خطا)
def simple_extract_pdf(uploaded_files):
    combined_text = ""
    for file in uploaded_files:
        file.seek(0) # بازگشت به ابتدای فایل
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            combined_text += page.get_text()
        doc.close()
    return combined_text

# ۳. رابط کاربری
st.title("🎓 سامانه هوشمند دانشگاه ملی مهارت")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# پنل کناری برای آپلود
with st.sidebar:
    st.header("فایل‌های آموزشی")
    uploaded_files = st.file_uploader("فایل‌های PDF را انتخاب کنید", type="pdf", accept_multiple_files=True)
    
    if st.button("🚀 شروع تحلیل فایل‌ها"):
        if uploaded_files:
            with st.spinner("در حال خواندن فایل‌ها..."):
                text = simple_extract_pdf(uploaded_files)
                st.session_state.extracted_text = text
                st.success(f"تحلیل انجام شد! {len(text)} کاراکتر استخراج شد.")
        else:
            st.warning("لطفاً ابتدا فایل آپلود کنید.")

# بخش چت
st.subheader("💬 گفتگو با دستیار هوشمند")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("سوال خود را بپرسید..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ترکیب متن PDF با سوال کاربر
            context = st.session_state.extracted_text[:10000] # محدودیت برای سرعت بیشتر
            full_prompt = f"متن مرجع: {context}\n\nسوال کاربر: {prompt}"
            
            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[
                    {"role": "system", "content": "تو دستیار دقیق دانشگاه هستی."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            answer = response.choices[0].message.content
            st.write(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"خطا در هوش مصنوعی: {str(e)}")
