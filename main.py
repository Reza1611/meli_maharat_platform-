import streamlit as st
import os
import sys

# مدیریت مسیرها
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import pandas as pd
import database as db
from utils.pdf_handler import extract_text_from_pdfs
from utils.ai_engine import generate_chat_response, test_api_key

# تنظیمات صفحه
st.set_page_config(page_title="سامانه هوشمند دانشگاه", page_icon="💎", layout="wide")
db.init_db()

# --- CSS حرفه‌ای و پیشرفته ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; }
    .stApp { background: #0f172a; color: #e2e8f0; }
    .top-bar {
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 15px;
        padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;
    }
    .welcome-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 20px;
        padding: 25px; margin-bottom: 20px; text-align: center;
    }
    .stButton>button {
        border-radius: 12px; transition: all 0.3s;
        background: linear-gradient(90deg, #2563eb, #3b82f6); color: white; border: none;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
</style>
""", unsafe_allow_html=True)

if "authentication_status" not in st.session_state:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center; margin-top:50px;'>ورود به سامانه هوشمند</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["ورود به حساب", "عضویت جدید"])
        with t1:
            u = st.text_input("نام کاربری")
            p = st.text_input("رمز عبور", type="password")
            if st.button("ورود", use_container_width=True):
                ok, user = db.verify_user(u, p)
                if ok:
                    st.session_state.authentication_status = True
                    st.session_state.user = user
                    st.rerun()
                else: st.error("اطلاعات نادرست است.")
else:
    # هدر داشبورد
    user = st.session_state.user
    st.markdown(f"""
    <div class="top-bar">
        <div><strong>{user['name']} خوش آمدید</strong></div>
        <div style="color: #4ade80;">وضعیت سیستم: عملیاتی ✅</div>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_tools = st.columns([1.6, 1], gap="large")

    with col_tools:
        st.markdown("### 📂 مدیریت اسناد")
        files = st.file_uploader("فایل‌های PDF اسناد دانشگاه", type="pdf", accept_multiple_files=True)
        if st.button("🔍 تحلیل اسناد", use_container_width=True):
            if files:
                with st.spinner("در حال استخراج متن..."):
                    txt, names = extract_text_from_pdfs(files)
                    st.session_state.pdf_text = txt
                    st.success(f"{len(names)} فایل بارگذاری شد.")
            else: st.error("فایلی انتخاب نشده است.")
        
        if st.sidebar.button("خروج از سیستم"):
            del st.session_state.authentication_status
            st.rerun()

    with col_chat:
        st.markdown("### 💬 گفتگو با دستیار")
        chat_container = st.container(height=500)
        
        if "messages" not in st.session_state: st.session_state.messages = []
        
        with chat_container:
            if not st.session_state.messages:
                st.markdown('<div class="welcome-card">فایل‌های PDF را آپلود کنید و سوالات خود را بپرسید.</div>', unsafe_allow_html=True)
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("سوال خود را اینجا بنویسید..."):
            if "pdf_text" not in st.session_state:
                st.warning("⚠️ ابتدا فایل‌ها را در سمت راست آپلود و دکمه تحلیل را بزنید.")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("در حال بررسی اسناد..."):
                            response = generate_chat_response(st.session_state.messages, st.session_state.pdf_text)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            db.add_question(user['username'], prompt, len(st.session_state.pdf_text))
                            st.rerun()
